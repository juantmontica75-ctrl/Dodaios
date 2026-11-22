"""Help text and hints name the command the person typed.

``jmxs`` is the command. JMXS declares no earlier command names, so usage
lines and "run this next" hints always say ``jmxs``, whatever name the process
was started under.
"""

from __future__ import annotations

import re
import sys

import pytest

import dodaios.__main__ as entry
from dodaios import __version__
from dodaios.cli import app_update
from dodaios.cli.command_name import main_command
from dodaios.core.branding import (
    CLI_COMMAND_NAME,
    CONTROL_CLI_COMMAND_NAME,
    LEGACY_CLI_COMMAND_NAMES,
)


@pytest.mark.parametrize(
    ("argv0", "expected"),
    [
        (CLI_COMMAND_NAME, CLI_COMMAND_NAME),
        (f"/home/u/.local/bin/{CLI_COMMAND_NAME}", CLI_COMMAND_NAME),
        (f"/home/u/.local/bin/{CLI_COMMAND_NAME}.exe", CLI_COMMAND_NAME),
        # Anything else is not a command name of ours: the primary name. A
        # Dodaios or Jarvis command name is not ours either.
        ("dodaios", CLI_COMMAND_NAME),
        ("/usr/bin/personal-jarvis", CLI_COMMAND_NAME),
        ("/repo/dodaios/__main__.py", CLI_COMMAND_NAME),
        (f"/opt/venv/bin/{CONTROL_CLI_COMMAND_NAME}", CLI_COMMAND_NAME),
        ("-c", CLI_COMMAND_NAME),
        ("", CLI_COMMAND_NAME),
    ],
)
def test_the_command_name_follows_how_the_process_was_started(argv0: str, expected: str) -> None:
    assert main_command(argv0) == expected


@pytest.mark.skipif(sys.platform != "win32", reason="backslash paths are Windows paths")
@pytest.mark.parametrize(
    ("argv0", "expected"),
    [
        (rf"C:\Users\u\.jmxs\bin\{CLI_COMMAND_NAME}.exe", CLI_COMMAND_NAME),
        (rf"C:\Users\u\.jmxs\bin\{CLI_COMMAND_NAME.upper()}.EXE", CLI_COMMAND_NAME),
        (r"C:\Program Files\JMXS\JMXS.exe", CLI_COMMAND_NAME),
    ],
)
def test_the_command_name_is_read_from_a_windows_launcher_path(argv0: str, expected: str) -> None:
    assert main_command(argv0) == expected


def test_the_primary_name_is_the_branding_constant() -> None:
    assert main_command("") == CLI_COMMAND_NAME == "jmxs"
    assert CONTROL_CLI_COMMAND_NAME == "jmxsctl"
    assert LEGACY_CLI_COMMAND_NAMES == ()


def test_the_launcher_help_names_the_invoked_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    command = CLI_COMMAND_NAME
    monkeypatch.setattr(sys, "argv", [f"/usr/local/bin/{command}", "--help"])

    parser = entry._build_parser()

    assert parser.prog == command
    # Without styling or layout: a newer argparse colours help on a terminal.
    help_text = " ".join(re.sub(r"\x1b\[[0-9;]*m", "", parser.format_help()).split())
    assert help_text.startswith(f"usage: {command} ")
    assert f"`{command} update --check`" in help_text
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])
    assert capsys.readouterr().out.strip() == f"{command} {__version__}"


def test_the_launcher_help_uses_the_primary_name_when_run_as_a_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["/repo/dodaios/__main__.py"])

    assert entry._build_parser().prog == CLI_COMMAND_NAME
    assert app_update.build_parser().prog == f"{CLI_COMMAND_NAME} update"


def test_the_update_command_help_names_the_invoked_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", [CLI_COMMAND_NAME, "update", "--help"])

    assert app_update.build_parser().prog == f"{CLI_COMMAND_NAME} update"
