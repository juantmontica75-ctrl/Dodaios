"""The control CLI answers under every one of its names and repeats the one used.

``jmxsctl`` is the command, and ``jmxs <group> ...`` routes into the same
command tree. JMXS declares no earlier control-command names.
"""

from __future__ import annotations

import re
import sys

import pytest

import dodaios.__main__ as entry
from dodaios import __version__
from dodaios.cli_ctl.__main__ import app, build_root_command
from dodaios.core.branding import (
    CLI_COMMAND_NAME,
    CONTROL_CLI_COMMAND_NAME,
    PRODUCT_NAME,
)

_NAMES = [CONTROL_CLI_COMMAND_NAME, CLI_COMMAND_NAME]
_STYLE = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    """Help output without terminal styling or layout: CI renders it in colour."""
    return " ".join(_STYLE.sub("", text).split())


def test_the_control_app_is_named_after_the_primary_command() -> None:
    assert app.info.name == CONTROL_CLI_COMMAND_NAME == "jmxsctl"


@pytest.mark.parametrize("name", _NAMES)
def test_the_version_line_repeats_the_invoked_name(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    root = build_root_command(["version"])

    root.main(args=["version"], prog_name=name, standalone_mode=False)

    assert capsys.readouterr().out.strip() == f"{name} ({PRODUCT_NAME} {__version__})"


@pytest.mark.parametrize("name", _NAMES)
def test_the_usage_line_repeats_the_invoked_name(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    root = build_root_command(["--help"])

    root.main(args=["--help"], prog_name=name, standalone_mode=False)

    assert f"Usage: {name} [OPTIONS] COMMAND [ARGS]..." in _plain(capsys.readouterr().out)


@pytest.mark.parametrize(
    ("argv0", "expected"),
    [(f"/usr/local/bin/{CLI_COMMAND_NAME}", CLI_COMMAND_NAME)],
)
def test_a_control_command_through_the_launcher_keeps_the_typed_name(
    argv0: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", [argv0, "version"])

    assert entry._run_control(["version"]) == 0

    assert capsys.readouterr().out.strip() == f"{expected} ({PRODUCT_NAME} {__version__})"
