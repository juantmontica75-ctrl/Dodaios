"""OmniRoute is a self-hosted OpenAI-compatible gateway, wired like LiteLLM.

The card stores a server URL (default http://localhost:20128/v1), the key is an
OmniRoute endpoint key, and the catalog is whatever the gateway lists.
"""
from __future__ import annotations

import io
from typing import Any

import pytest

import dodaios.core.config as cfg
from dodaios.brain.manager import PROVIDER_ALIASES, TIER_DEFAULTS_BY_PROVIDER
from dodaios.brain.model_catalog import CATALOG_PROVIDERS, _ENDPOINTS, ModelCatalog
from dodaios.brain.provider_registry import BrainProviderRegistry
from dodaios.core.config import BrainConfig, BrainProviderConfig, JarvisConfig
from dodaios.core.protocols import BrainMessage, BrainRequest
from dodaios.missions.init import _API_AGENT_SLUGS
from dodaios.missions.worker_runtime.provider_map import env_vars_for, to_worker_slug
from dodaios.missions.workers.api_agent_worker import (
    _BRAIN_BY_PROVIDER,
    supports_api_agent_worker,
)
from dodaios.plugins.brain import omniroute_cli
from dodaios.plugins.brain.omniroute import (
    BASE_URL,
    OmniRouteBrain,
    OmniRouteURLError,
    endpoint_url,
    first_chat_model,
)
from dodaios.ui.web.provider_spec import get_spec
from tests.fakes.provider_config import install_provider_config


class _FakeOpenAI:
    last_kwargs: dict[str, Any] = {}

    def __init__(self, **kwargs: Any) -> None:
        type(self).last_kwargs = kwargs


def test_omniroute_is_a_registered_brain_plugin() -> None:
    reg = BrainProviderRegistry()
    assert "omniroute" in reg.available()
    assert "omniroute" not in reg.failed()
    brain = reg.instantiate("omniroute")
    assert brain.name == "omniroute"
    assert brain.can_call_tools() is True


def test_omniroute_credential_slot_resolves() -> None:
    assert cfg.PROVIDER_SECRET_CANDIDATES["omniroute"][0] == (
        "omniroute_api_key",
        "OMNIROUTE_API_KEY",
    )
    assert cfg.JARVIS_AGENT_SECRET_CANDIDATES["omniroute"][0][0] == (
        "jarvis_agent_omniroute_api_key"
    )


def test_omniroute_provider_spec_has_a_host_field() -> None:
    spec = get_spec("omniroute")
    assert spec is not None
    assert spec.tier == "brain"
    assert spec.auth_mode == "api_key"
    assert spec.secret_keys == ("omniroute_api_key",)
    assert spec.brain_switchable is True
    assert spec.supports_base_url is True
    assert spec.default_base_url == BASE_URL == "http://localhost:20128/v1"


def test_omniroute_catalog_endpoint() -> None:
    assert "omniroute" in CATALOG_PROVIDERS
    ep = _ENDPOINTS["omniroute"]
    assert ep.auth == "bearer"
    assert ep.vendor_base + ep.path == "http://localhost:20128/v1/models"


async def test_omniroute_catalog_uses_the_saved_host(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    class _Response:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return {"data": [{"id": "cc/claude-sonnet"}]}

    class _Client:
        def __init__(self) -> None:
            self.calls: list[str] = []

        async def __aenter__(self) -> _Client:
            return self

        async def __aexit__(self, *exc: object) -> None:
            return None

        async def get(self, url: str, headers=None, params=None) -> _Response:
            self.calls.append(url)
            return _Response()

    client = _Client()
    install_provider_config(
        monkeypatch,
        JarvisConfig(
            brain=BrainConfig(
                providers={"omniroute": BrainProviderConfig(base_url="http://gw.lan:20128")}
            )
        ),
    )
    monkeypatch.setattr(cfg, "get_provider_secret", lambda pid: "sk-omni")
    catalog = ModelCatalog(cache_path=tmp_path / "cache.json", http_client_factory=lambda: client)
    result = await catalog.list_models("omniroute")
    assert result.source == "live"
    assert [m.id for m in result.models] == ["cc/claude-sonnet"]
    assert client.calls == ["http://gw.lan:20128/v1/models"]


def test_omniroute_client_uses_default_host(monkeypatch: pytest.MonkeyPatch) -> None:
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", _FakeOpenAI)
    install_provider_config(monkeypatch, JarvisConfig())
    monkeypatch.setattr(cfg, "get_provider_secret", lambda pid: "sk-omni")
    OmniRouteBrain()._ensure_client()
    assert _FakeOpenAI.last_kwargs["base_url"] == BASE_URL
    assert _FakeOpenAI.last_kwargs["api_key"] == "sk-omni"


def test_omniroute_client_adds_v1_to_a_saved_root(monkeypatch: pytest.MonkeyPatch) -> None:
    import openai

    monkeypatch.setattr(openai, "AsyncOpenAI", _FakeOpenAI)
    install_provider_config(
        monkeypatch,
        JarvisConfig(
            brain=BrainConfig(
                providers={"omniroute": BrainProviderConfig(base_url="http://gw.lan:20128")}
            )
        ),
    )
    monkeypatch.setattr(cfg, "get_provider_secret", lambda pid: "sk-omni")
    OmniRouteBrain()._ensure_client()
    assert _FakeOpenAI.last_kwargs["base_url"] == "http://gw.lan:20128/v1"


def test_omniroute_without_key_fails_with_guidance(monkeypatch: pytest.MonkeyPatch) -> None:
    install_provider_config(monkeypatch, JarvisConfig())
    monkeypatch.setattr(cfg, "get_provider_secret", lambda pid: None)
    with pytest.raises(RuntimeError, match="jmxs-gateway key"):
        OmniRouteBrain()._ensure_client()


def test_omniroute_tier_default_is_discovered() -> None:
    assert TIER_DEFAULTS_BY_PROVIDER["router"]["omniroute"] == ""
    assert TIER_DEFAULTS_BY_PROVIDER["deep"]["omniroute"] == ""
    assert PROVIDER_ALIASES["omniroute"] == "omniroute"


def test_omniroute_unknown_model_cannot_see(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dodaios.brain.model_catalog.model_capabilities",
        lambda provider, model: {"vision": None, "tools": None},
    )
    monkeypatch.setattr(
        "dodaios.brain.model_catalog.model_context_length", lambda provider, model: None,
    )
    assert OmniRouteBrain(model="local-route").supports_vision is False


async def test_omniroute_complete_caps_the_reply(monkeypatch: pytest.MonkeyPatch) -> None:
    brain = OmniRouteBrain(model="auto")
    brain.context_window = 8192
    seen: dict[str, object] = {}

    async def _model(_client: object) -> str:
        return "auto"

    async def _stream(_client: object, model: str, req: BrainRequest, **kwargs: object):
        seen["model"] = model
        seen["max_tokens"] = req.max_tokens
        if False:
            yield None

    monkeypatch.setattr(brain, "_ensure_client", lambda: object())
    monkeypatch.setattr(brain, "_resolve_model", _model)
    monkeypatch.setattr("dodaios.plugins.brain.omniroute.stream_complete", _stream)
    req = BrainRequest(messages=(BrainMessage(role="user", content="hi"),), max_tokens=32_768)
    async for _delta in brain.complete(req):
        pass
    assert seen["model"] == "auto"
    assert int(seen["max_tokens"]) <= 8192


def test_omniroute_discovery_skips_non_chat_models() -> None:
    assert first_chat_model(["text-embedding-3-small", "auto"]) == "auto"
    assert first_chat_model(["text-embedding-3-small"]) == ""


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("http://localhost:20128", "http://localhost:20128/v1"),
        ("http://localhost:20128/v1/", "http://localhost:20128/v1"),
        ("http://0.0.0.0:20128", "http://localhost:20128/v1"),
        ("https://gw.example.com", "https://gw.example.com/v1"),
    ],
)
def test_endpoint_url_normalizes(raw: str, expected: str) -> None:
    assert endpoint_url(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "ftp://host", "localhost:20128", "http://user:pw@host", "http://h/v1?key=x", "http://h#f"],
)
def test_endpoint_url_rejects_unsafe(raw: str) -> None:
    with pytest.raises(OmniRouteURLError):
        endpoint_url(raw)


def test_omniroute_is_an_agent_provider() -> None:
    from dodaios.agent_chat.catalog import offers
    from dodaios.agent_chat.runner_api import supports_api_runner

    assert offers("society", "omniroute")
    assert supports_api_runner("omniroute")
    assert "omniroute" in _API_AGENT_SLUGS
    assert supports_api_agent_worker("omniroute") is True
    assert "omniroute" in _BRAIN_BY_PROVIDER
    assert to_worker_slug("omniroute") == "omniroute"
    assert "OMNIROUTE_API_KEY" in env_vars_for("omniroute")


# ── jmxs-gateway CLI ────────────────────────────────────────────────────


class _NonTTY(io.StringIO):
    def isatty(self) -> bool:
        return False


def test_cli_key_reads_stdin_and_never_prints_it(monkeypatch: pytest.MonkeyPatch) -> None:
    stored: dict[str, str] = {}
    monkeypatch.setattr(cfg, "set_secret", lambda k, v: stored.update({k: v}) or True)
    out = io.StringIO()
    code = omniroute_cli.main(["key"], out=out, stdin=_NonTTY("sk-omni-secret\n"))
    assert code == 0
    assert stored == {"omniroute_api_key": "sk-omni-secret"}
    assert "sk-omni-secret" not in out.getvalue()


def test_cli_key_rejects_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cfg, "set_secret", lambda k, v: pytest.fail("must not store"))
    assert omniroute_cli.main(["key"], out=io.StringIO(), stdin=_NonTTY("\n")) == 2


def test_cli_key_is_not_an_argument() -> None:
    with pytest.raises(SystemExit):
        omniroute_cli.main(["key", "sk-in-argv"], out=io.StringIO())


def test_cli_url_validates_and_saves(monkeypatch: pytest.MonkeyPatch) -> None:
    from dodaios.core import config_writer

    saved: list[tuple[str, str | None]] = []
    monkeypatch.setattr(config_writer, "set_provider_base_url", lambda p, u: saved.append((p, u)))
    assert omniroute_cli.main(["url", "http://gw.lan:20128"], out=io.StringIO()) == 0
    assert saved == [("omniroute", "http://gw.lan:20128/v1")]
    assert omniroute_cli.main(["url", "http://u:p@gw"], out=io.StringIO()) == 2
    assert len(saved) == 1


def test_cli_select_verifies_against_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    from dodaios.core import config_writer

    picks: list[tuple[str, str]] = []
    primaries: list[str] = []
    monkeypatch.setattr(omniroute_cli, "list_gateway_models", lambda url, key: ["auto", "kr/x"])
    monkeypatch.setattr(omniroute_cli, "_configured_url", lambda: BASE_URL)
    monkeypatch.setattr(cfg, "get_provider_secret", lambda pid: "sk")
    monkeypatch.setattr(
        config_writer, "set_brain_provider_model",
        lambda provider, model=None, **kw: picks.append((provider, model)),
    )
    monkeypatch.setattr(config_writer, "set_brain_primary", lambda name: primaries.append(name))
    assert omniroute_cli.main(["select", "missing"], out=io.StringIO()) == 1
    assert picks == []
    assert omniroute_cli.main(["select", "auto", "--primary"], out=io.StringIO()) == 0
    assert picks == [("omniroute", "auto")]
    assert primaries == ["omniroute"]


def test_cli_show_never_prints_the_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cfg, "get_provider_secret", lambda pid: "sk-omni-secret")
    monkeypatch.setattr(omniroute_cli, "_configured_url", lambda: BASE_URL)
    monkeypatch.setattr(omniroute_cli, "_configured_model", lambda: "auto")
    monkeypatch.setattr(omniroute_cli, "_primary_brain", lambda: "omniroute")
    out = io.StringIO()
    assert omniroute_cli.main(["show"], out=out) == 0
    text = out.getvalue()
    assert "sk-omni-secret" not in text
    assert "configured" in text and "auto" in text and "primary:  yes" in text
