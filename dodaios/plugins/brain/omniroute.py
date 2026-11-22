"""OmniRoute — a self-hosted, OpenAI-compatible AI gateway.

OmniRoute runs on the user's machine (default ``http://localhost:20128``) and
routes one OpenAI-shaped API to every provider connected in its dashboard.
The key is an OmniRoute endpoint key (Dashboard -> Endpoints), never an
upstream vendor key: upstream credentials stay inside OmniRoute.

Wired like the LiteLLM proxy: the card stores a server URL, the catalog is the
gateway's own ``/v1/models`` list, and a model-less brain asks the gateway
which chat model to use.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from dodaios.core import config as cfg
from dodaios.core.protocols import BrainDelta, BrainRequest

from ._openai_base import CLIENT_TIMEOUT, stream_complete
from .litellm import fit_reply_cap, openai_client_base, openai_server_root

log = logging.getLogger(__name__)

PROVIDER_ID = "omniroute"
DISPLAY_NAME = "OmniRoute"
BASE_URL = "http://localhost:20128/v1"
DASHBOARD_URL = "http://localhost:20128/dashboard"
SECRET_SLOT = "omniroute_api_key"
SECRET_ENV = "OMNIROUTE_API_KEY"

# Until the gateway reports the selected model's window. Small on purpose:
# OmniRoute may front a small local model, and a 128k guess sends the full
# tool list it would refuse.
_UNPUBLISHED_WINDOW = 32_768


class OmniRouteURLError(ValueError):
    """A server URL that cannot be an OmniRoute endpoint."""


def endpoint_url(url: str) -> str:
    """Normalize a pasted OmniRoute address to the OpenAI client base (``.../v1``).

    Accepts the bare root (``http://host:20128``) or the client base. Rejects
    anything that is not plain http(s), and anything carrying credentials, a
    query or a fragment, so a key can never be smuggled into the stored URL.
    """
    from urllib.parse import urlsplit

    raw = (url or "").strip()
    if not raw:
        raise OmniRouteURLError("The OmniRoute URL is empty.")
    parts = urlsplit(raw)
    if parts.scheme not in ("http", "https"):
        raise OmniRouteURLError("The OmniRoute URL must start with http:// or https://.")
    if not parts.hostname:
        raise OmniRouteURLError("The OmniRoute URL has no host.")
    if parts.username or parts.password:
        raise OmniRouteURLError("Do not put credentials in the URL; use `jmxs-gateway key`.")
    if parts.query or parts.fragment:
        raise OmniRouteURLError("The OmniRoute URL must not contain a query or fragment.")
    cleaned = raw.rstrip("/").replace("://0.0.0.0", "://localhost", 1)
    return openai_client_base(cleaned)


def chat_model_ids(ids: list[str]) -> list[str]:
    """The ids the model picker would offer, in picker order."""
    from dodaios.brain.model_catalog import ModelInfo, filter_brain_models, sort_models

    infos = [ModelInfo(id=name, label=name) for name in ids if name]
    return [m.id for m in sort_models(PROVIDER_ID, filter_brain_models(infos))]


def first_chat_model(ids: list[str]) -> str:
    """The first id the model picker would offer, or ``""`` when none qualify."""
    usable = chat_model_ids(ids)
    return usable[0] if usable else ""


def list_gateway_models(base_url: str, api_key: str | None, *, timeout: float = 5.0) -> list[str]:
    """Every model id the gateway lists at ``{base}/models``. Raises on HTTP errors."""
    import httpx

    url = endpoint_url(base_url) + "/models"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    response = httpx.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    rows = response.json().get("data") or []
    return [
        str(row.get("id") or "").strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("id") or "").strip()
    ]


class OmniRouteBrain:
    name: str = PROVIDER_ID
    context_window: int = _UNPUBLISHED_WINDOW
    supports_tools: bool = True
    # Unknown stays blind. A catalog entry that declares image input turns it on.
    supports_vision: bool = False

    def __init__(self, model: str | None = None) -> None:
        self._model = (model or "").strip()
        self._client: Any = None
        self._api_key: str | None = None
        try:
            from dodaios.brain.model_catalog import model_capabilities, model_context_length

            caps = model_capabilities(PROVIDER_ID, self._model) if self._model else {}
            if caps:
                if caps.get("vision") is not None:
                    self.supports_vision = bool(caps["vision"])
                if caps.get("tools") is not None:
                    self.supports_tools = bool(caps["tools"])
            cached = model_context_length(PROVIDER_ID, self._model) if self._model else None
            if cached:
                self.context_window = cached
        except Exception:  # noqa: BLE001 — a capability probe must never break construction
            pass
        if self._model:
            from dodaios.brain import local_context

            seen = local_context.known_window_for_model(self.name, self._model)
            if seen:
                self.context_window = seen

    def can_call_tools(self) -> bool:
        return self.supports_tools

    def _ensure_client(self) -> Any:
        if self._client is None:
            ep = cfg.resolve_provider_endpoint(PROVIDER_ID, vendor_default_base_url=BASE_URL)
            if not ep.credential:
                raise RuntimeError(
                    f"No OmniRoute API key found ({SECRET_SLOT} / {SECRET_ENV}). "
                    "Create one in the OmniRoute dashboard (Endpoints) and save it "
                    "with `jmxs-gateway key`."
                )
            if not ep.base_url:
                raise RuntimeError(
                    "OmniRoute needs a server URL — set it on the provider card "
                    f"(usually {BASE_URL})."
                )
            from openai import AsyncOpenAI

            self._api_key = ep.credential
            base_url = ep.base_url if ep.via_proxy else openai_client_base(ep.base_url or "")
            self._client = AsyncOpenAI(
                api_key=ep.credential,
                base_url=base_url,
                timeout=CLIENT_TIMEOUT,
            )
        return self._client

    async def _resolve_model(self, client: Any) -> str:
        """The configured model, else the first chat model the gateway lists."""
        if self._model:
            return self._model
        try:
            listed = await client.models.list()
        except Exception as exc:
            raise RuntimeError(
                "OmniRoute has no model selected and the gateway did not answer "
                "/models. Check that OmniRoute is running, the URL and the key, "
                "or pick a model with `jmxs-gateway select`."
            ) from exc
        names = [
            str(getattr(item, "id", "") or "").strip()
            for item in (getattr(listed, "data", None) or [])
        ]
        chosen = first_chat_model(names)
        if not chosen:
            raise RuntimeError(
                "OmniRoute lists no chat models. Connect a provider in the "
                "OmniRoute dashboard, then pick a model."
            )
        self._model = chosen
        return self._model

    async def prepare_context_window(self) -> None:
        """Size the tool list from the gateway's window before the turn is sent.

        Never raises: a silent gateway is budgeted small instead of refusing the turn.
        """
        if not self._model:
            return
        try:
            client = await asyncio.to_thread(self._ensure_client)
            root = openai_server_root(str(getattr(client, "base_url", "") or ""))
            headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
            from dodaios.brain import local_context

            window = await local_context.probe_server_window(
                root, self._model, headers=headers, provider=self.name,
            )
        except Exception as exc:  # noqa: BLE001 — sizing must never cost the turn
            log.debug("omniroute: could not settle the context window early: %s", exc)
            return
        if window is not None and window.tokens:
            self.context_window = window.tokens

    async def complete(self, req: BrainRequest) -> AsyncIterator[BrainDelta]:
        client = self._client
        if client is None:
            client = await asyncio.to_thread(self._ensure_client)
        model = await self._resolve_model(client)
        req = fit_reply_cap(req, self.context_window)
        async for delta in stream_complete(
            client, model, req, supports_vision=self.supports_vision,
        ):
            yield delta

    def estimate_cost(self, req: BrainRequest) -> float:
        # The real price depends on the upstream behind the route. A conservative
        # stand-in, the same shape as the other gateway brains.
        in_tokens = sum(len(str(m.content)) for m in req.messages) // 4
        return (in_tokens * 10 + req.max_tokens * 30) / 1_000_000
