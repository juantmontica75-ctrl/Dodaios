"""``jmxs-gateway`` — connect JMXS to an OmniRoute gateway from the terminal.

Subcommands::

    jmxs-gateway url [URL]          show or set the OmniRoute server URL
    jmxs-gateway key                save the OmniRoute API key (read from stdin / prompt)
    jmxs-gateway forget-key         delete the saved key
    jmxs-gateway models             list the chat models the gateway serves
    jmxs-gateway select MODEL       use MODEL for OmniRoute (add --primary to make
                                    OmniRoute the main brain)
    jmxs-gateway clear-selection    forget the selected model (auto-discover again)
    jmxs-gateway show               print the current connection, never the key

The key is never accepted as a command-line argument (it would land in shell
history and the process list) and is never printed.
"""
from __future__ import annotations

import argparse
import getpass
import sys
from collections.abc import Callable, Sequence
from typing import TextIO

from dodaios.plugins.brain.omniroute import (
    BASE_URL,
    DISPLAY_NAME,
    PROVIDER_ID,
    SECRET_SLOT,
    OmniRouteURLError,
    chat_model_ids,
    endpoint_url,
    list_gateway_models,
)


def _configured_url() -> str:
    from dodaios.core import config as cfg

    ep = cfg.resolve_provider_endpoint(PROVIDER_ID, vendor_default_base_url=BASE_URL)
    return ep.base_url or BASE_URL


def _configured_model() -> str:
    from dodaios.core import config as cfg

    try:
        provider = cfg.load_config().brain.providers.get(PROVIDER_ID)
    except Exception:  # noqa: BLE001 — a broken config still lets `show` answer
        return ""
    return (getattr(provider, "model", None) or "").strip()


def _primary_brain() -> str:
    from dodaios.core import config as cfg

    try:
        return str(cfg.load_config().brain.primary or "")
    except Exception:  # noqa: BLE001
        return ""


def _read_key(stdin: TextIO, prompt: Callable[[str], str]) -> str:
    if stdin.isatty():
        return prompt("OmniRoute API key: ").strip()
    return stdin.readline().strip()


def _cmd_url(args: argparse.Namespace, out: TextIO) -> int:
    if not args.url:
        print(_configured_url(), file=out)
        return 0
    from dodaios.core import config_writer

    cleaned = endpoint_url(args.url)
    config_writer.set_provider_base_url(PROVIDER_ID, cleaned)
    print(f"{DISPLAY_NAME} URL set to {cleaned}", file=out)
    return 0


def _cmd_key(args: argparse.Namespace, out: TextIO, stdin: TextIO,
             prompt: Callable[[str], str]) -> int:
    from dodaios.core import config as cfg

    key = _read_key(stdin, prompt)
    if not key:
        print("No key given; nothing saved.", file=sys.stderr)
        return 2
    if any(ch.isspace() for ch in key):
        print("The key must not contain whitespace; nothing saved.", file=sys.stderr)
        return 2
    if not cfg.set_secret(SECRET_SLOT, key):
        print("Could not store the key in the credential store.", file=sys.stderr)
        return 1
    print(f"{DISPLAY_NAME} key saved to the credential store.", file=out)
    return 0


def _cmd_forget_key(args: argparse.Namespace, out: TextIO) -> int:
    from dodaios.core import config as cfg

    cfg.delete_secret(SECRET_SLOT)
    print(f"{DISPLAY_NAME} key removed.", file=out)
    return 0


def _cmd_models(args: argparse.Namespace, out: TextIO) -> int:
    from dodaios.core import config as cfg

    ids = list_gateway_models(_configured_url(), cfg.get_provider_secret(PROVIDER_ID))
    shown = ids if args.all else chat_model_ids(ids)
    selected = _configured_model()
    for model_id in shown:
        marker = "*" if model_id == selected else " "
        print(f"{marker} {model_id}", file=out)
    if not shown:
        print("The gateway lists no chat models.", file=sys.stderr)
        return 1
    return 0


def _cmd_select(args: argparse.Namespace, out: TextIO) -> int:
    from dodaios.core import config as cfg
    from dodaios.core import config_writer

    model = args.model.strip()
    if not model:
        print("Model id is empty.", file=sys.stderr)
        return 2
    if not args.no_verify:
        ids = list_gateway_models(_configured_url(), cfg.get_provider_secret(PROVIDER_ID))
        if model not in ids:
            print(
                f"'{model}' is not served by the gateway. Run `jmxs-gateway models`, "
                "or pass --no-verify.",
                file=sys.stderr,
            )
            return 1
    config_writer.set_brain_provider_model(PROVIDER_ID, model=model)
    if args.primary:
        config_writer.set_brain_primary(PROVIDER_ID)
    suffix = " and set as the main brain" if args.primary else ""
    print(f"{DISPLAY_NAME} model set to {model}{suffix}.", file=out)
    return 0


def _cmd_clear_selection(args: argparse.Namespace, out: TextIO) -> int:
    from dodaios.core import config_writer

    config_writer.set_brain_provider_model(PROVIDER_ID, model="")
    print(f"{DISPLAY_NAME} model cleared; the first chat model will be used.", file=out)
    return 0


def _cmd_show(args: argparse.Namespace, out: TextIO) -> int:
    from dodaios.core import config as cfg

    has_key = bool(cfg.get_provider_secret(PROVIDER_ID))
    print(f"provider: {PROVIDER_ID}", file=out)
    print(f"url:      {_configured_url()}", file=out)
    print(f"key:      {'configured' if has_key else 'missing'}", file=out)
    print(f"model:    {_configured_model() or '(auto)'}", file=out)
    print(f"primary:  {'yes' if _primary_brain() == PROVIDER_ID else 'no'}", file=out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jmxs-gateway", description="Connect JMXS to an OmniRoute gateway."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    url = sub.add_parser("url", help="show or set the OmniRoute server URL")
    url.add_argument("url", nargs="?", default="")
    sub.add_parser("key", help="save the OmniRoute API key (stdin or prompt)")
    sub.add_parser("forget-key", help="delete the saved OmniRoute API key")
    models = sub.add_parser("models", help="list the models the gateway serves")
    models.add_argument("--all", action="store_true", help="include non-chat models")
    select = sub.add_parser("select", help="use a model for OmniRoute")
    select.add_argument("model")
    select.add_argument("--primary", action="store_true", help="also make OmniRoute the main brain")
    select.add_argument("--no-verify", action="store_true", help="skip the gateway check")
    sub.add_parser("clear-selection", help="forget the selected model")
    sub.add_parser("show", help="print the current connection (never the key)")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    out: TextIO | None = None,
    stdin: TextIO | None = None,
    prompt: Callable[[str], str] = getpass.getpass,
) -> int:
    out = out or sys.stdout
    stdin = stdin or sys.stdin
    args = build_parser().parse_args(argv)
    handlers: dict[str, Callable[[], int]] = {
        "url": lambda: _cmd_url(args, out),
        "key": lambda: _cmd_key(args, out, stdin, prompt),
        "forget-key": lambda: _cmd_forget_key(args, out),
        "models": lambda: _cmd_models(args, out),
        "select": lambda: _cmd_select(args, out),
        "clear-selection": lambda: _cmd_clear_selection(args, out),
        "show": lambda: _cmd_show(args, out),
    }
    try:
        return handlers[args.command]()
    except OmniRouteURLError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — a CLI reports, it does not trace back
        import httpx

        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            hint = " (check the key)" if status in (401, 403) else ""
            print(f"OmniRoute answered HTTP {status}{hint}.", file=sys.stderr)
            return 1
        if isinstance(exc, httpx.HTTPError):
            print(f"Could not reach OmniRoute at {_configured_url()}: {type(exc).__name__}.",
                  file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())
