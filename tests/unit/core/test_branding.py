"""Freeze the JMXS product identity.

JMXS is an independent fork of Dodaios. Every persistent identifier is a JMXS
name, and no ``LEGACY_*`` tuple lets this install find, adopt, migrate or
delete anything a Dodaios (or Personal Jarvis) installation owns.
"""

from __future__ import annotations

import importlib
import os

import pytest

import dodaios.core.branding as branding

_CURRENT_IDENTITY = {
    "PERSISTENT_PRODUCT_NAME": 'JMXS Desktop',
    "PERSISTENT_COMPACT_NAME": 'JMXSDesktop',
    "PERSISTENT_SLUG": 'jmxs-desktop',
    "PRODUCT_COMPACT_NAME": 'JMXSDesktop',
    "PRODUCT_SLUG": 'jmxs-desktop',
    "LAUNCHER_ENTRY_NAME": 'JMXS',
    "LEGACY_LAUNCHER_ENTRY_NAMES": (),
    "CONFIG_FILE_NAME": 'jmxs.toml',
    "LEGACY_CONFIG_FILE_NAMES": (),
    "DISTRIBUTION_NAME": 'jmxs',
    "LEGACY_DISTRIBUTION_NAMES": (),
    "DISTRIBUTION_NAMES": ('jmxs',),
    "CLI_COMMAND_NAME": 'jmxs',
    "CONTROL_CLI_COMMAND_NAME": 'jmxsctl',
    "LEGACY_CLI_COMMAND_NAMES": (),
    "LEGACY_CONTROL_CLI_COMMAND_NAMES": (),
    "CLI_COMMAND_NAMES": ('jmxs', 'jmxsctl'),
    "SHELL_PROFILE_MARKER": '# JMXS Desktop: command-line tools (jmxs, jmxsctl)',
    "FISH_CONF_FILE_NAME": 'jmxs-desktop.fish',
    "KEYRING_SERVICE_NAME": 'jmxs',
    "LEGACY_KEYRING_SERVICE_NAMES": (),
    "CONTROL_KEY_PREFIX": 'jmxsctl_',
    "SESSION_COOKIE_NAME": 'jmxs_session',
    "MANAGED_INSTALL_MARKER": '.jmxs-managed-install',
    "LEGACY_MANAGED_INSTALL_MARKERS": (),
    "MANAGED_INSTALL_MARKERS": ('.jmxs-managed-install',),
    "DEFAULT_INSTALL_DIR_NAME": '.jmxs',
    "LEGACY_DEFAULT_INSTALL_DIR_NAMES": (),
    "WINDOWS_USER_DATA_DIR_NAME": 'JMXS',
    "LEGACY_WINDOWS_USER_DATA_DIR_NAMES": (),
    "FALLBACK_USER_DATA_DIR_NAME": '.jmxs-data',
    "LEGACY_FALLBACK_USER_DATA_DIR_NAMES": (),
    "DESKTOP_OUTPUT_MIRROR_DIR_NAME": 'JMXS-Output',
    "LEGACY_DESKTOP_OUTPUT_MIRROR_DIR_NAMES": (),
    "DELIVERABLES_DIR_NAME": 'JMXS-Outputs',
    "LEGACY_DELIVERABLES_DIR_NAMES": (),
    "OBSIDIAN_VAULT_FOLDER_NAME": 'JMXS',
    "LEGACY_OBSIDIAN_VAULT_FOLDER_NAMES": (),
    "WINDOWS_MUTEX_NAME": 'Global\\JMXS_v1',
    "LEGACY_WINDOWS_MUTEX_NAMES": (),
    "WINDOWS_APP_USER_MODEL_ID": 'JMXSDesktop.JMXSDesktop',
    "WINDOWS_UNINSTALL_REGISTRY_SUBKEY": 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\JMXSDesktop',
    "WINDOWS_AUTOSTART_TASK_NAME": 'JMXS Autostart',
    "LEGACY_WINDOWS_AUTOSTART_TASK_NAMES": (),
    "WINDOWS_SHORTCUT_FILE_NAME": 'JMXS.lnk',
    "LEGACY_WINDOWS_SHORTCUT_FILE_NAMES": (),
    "WINDOWS_AUTOSTART_DESCRIPTION": 'JMXS (Autostart)',
    "LEGACY_WINDOWS_AUTOSTART_DESCRIPTIONS": (),
    "WINDOWS_BRANDED_LAUNCHER_FILE_NAME": 'JMXSApp.exe',
    "LEGACY_WINDOWS_BRANDED_LAUNCHER_FILE_NAMES": (),
    "WINDOWS_BRANDED_LAUNCHER_DIR_NAME": 'JMXSApp',
    "LEGACY_WINDOWS_BRANDED_LAUNCHER_DIR_NAMES": (),
    "WINDOWS_BRANDED_LAUNCH_ENV_VAR": 'JMXS_BRANDED_LAUNCH',
    "MACOS_APP_NAME": 'JMXS',
    "LEGACY_MACOS_APP_NAMES": (),
    "MACOS_APP_DIR_NAME": 'JMXS.app',
    "LEGACY_MACOS_APP_DIR_NAMES": (),
    "MACOS_APP_DIR_NAMES": ('JMXS.app',),
    "MACOS_EXECUTABLE_NAME": 'JMXSApp',
    "LEGACY_MACOS_EXECUTABLE_NAMES": (),
    "MACOS_BUNDLE_ID": 'com.jmxs-desktop.desktop',
    "MACOS_DMG_BUNDLE_ID": 'ai.jmxsdesktop.desktop',
    "MACOS_AUTOSTART_LABEL": 'com.jmxs-desktop.autostart',
    "MACOS_SIGNING_IDENTITY_LABEL": 'JMXS Desktop Local Signing',
    "LINUX_APP_NAME": 'JMXS',
    "LEGACY_LINUX_APP_NAMES": (),
    "LINUX_DESKTOP_ENTRY_FILE_NAME": 'jmxs.desktop',
    "LEGACY_LINUX_DESKTOP_ENTRY_FILE_NAMES": (),
    "LINUX_WM_CLASS": 'jmxs',
    "LEGACY_LINUX_WM_CLASSES": (),
    "DEFAULT_OFFICIAL_REPO_SLUG": 'juantmontica75-ctrl/Dodaios',
    "OFFICIAL_REPO_SLUG_ENV_VAR": 'JMXS_OFFICIAL_REPO_SLUG',
    "OFFICIAL_REPO_SLUG": 'juantmontica75-ctrl/Dodaios',
    "OFFICIAL_REPO_URL": 'https://github.com/juantmontica75-ctrl/Dodaios',
    "OFFICIAL_REPO_GIT_URL": 'https://github.com/juantmontica75-ctrl/Dodaios.git',
    "OFFICIAL_RELEASES_LATEST_API_URL": 'https://api.github.com/repos/juantmontica75-ctrl/Dodaios/releases/latest',
    "UPDATER_USER_AGENT": 'JMXS-Updater',
    "HTTP_USER_AGENT": 'JMXS/1.0',
}

# Names that would reach another product's files, credentials, tasks, bundles
# or processes. JMXS has no earlier generation, so every one of them is empty.
_LEGACY_TUPLES = sorted(
    name
    for name in dir(branding)
    if name.startswith("LEGACY_")
    and name
    not in {
        # Internal wire contracts shared with the code base, not install state.
        "LEGACY_PLUGIN_GROUP_NAMESPACES",
        "LEGACY_MARKETPLACE_EXTENSION_NAMESPACES",
        "LEGACY_IMPORT_NAMES",
        "LEGACY_PACKAGE_NAMES",
    }
)

# Spellings of a product other than JMXS. The repository slug is exempt: the
# fork is still hosted as ``juantmontica75-ctrl/Dodaios``.
_FOREIGN_SPELLINGS = ("dodaios", "jarvis")


def test_no_identifier_adopts_another_products_install() -> None:
    assert _LEGACY_TUPLES
    for name in _LEGACY_TUPLES:
        assert getattr(branding, name) == (), name


def test_default_exported_identity_values_are_frozen() -> None:
    previous = os.environ.pop(branding.OFFICIAL_REPO_SLUG_ENV_VAR, None)
    try:
        module = importlib.reload(branding)
        actual = {name: getattr(module, name) for name in _CURRENT_IDENTITY}
        assert actual == _CURRENT_IDENTITY
    finally:
        if previous is not None:
            os.environ[branding.OFFICIAL_REPO_SLUG_ENV_VAR] = previous
        importlib.reload(branding)


def test_identity_never_spells_another_product() -> None:
    for name in _CURRENT_IDENTITY:
        if "REPO" in name or "RELEASES" in name:
            continue
        value = str(getattr(branding, name)).casefold()
        for foreign in _FOREIGN_SPELLINGS:
            assert foreign not in value, name


def test_the_linux_names_move_as_one_generation() -> None:
    assert branding.LINUX_DESKTOP_ENTRY_FILE_NAME == f"{branding.LINUX_WM_CLASS}.desktop"
    assert branding.LEGACY_LINUX_DESKTOP_ENTRY_FILE_NAMES == ()
    assert branding.LEGACY_LINUX_WM_CLASSES == ()


def test_the_windows_launcher_folder_is_not_the_data_directory() -> None:
    assert (
        branding.WINDOWS_BRANDED_LAUNCHER_DIR_NAME.casefold()
        != branding.WINDOWS_USER_DATA_DIR_NAME.casefold()
    )
    assert branding.LEGACY_WINDOWS_MUTEX_NAMES == ()


def test_no_command_shares_a_file_with_the_branded_executable() -> None:
    # The branded executable sits beside the commands, and Windows and macOS
    # paths ignore case: a command spelled like it would be the same file.
    executables = {
        branding.WINDOWS_BRANDED_LAUNCHER_FILE_NAME.removesuffix(".exe").casefold(),
        branding.MACOS_EXECUTABLE_NAME.casefold(),
    }
    for command in branding.CLI_COMMAND_NAMES:
        assert command.casefold() not in executables, command


def test_the_macos_bundle_names_are_jmxs_only() -> None:
    assert branding.MACOS_BUNDLE_ID == "com.jmxs-desktop.desktop"
    assert branding.MACOS_APP_DIR_NAMES == (branding.MACOS_APP_DIR_NAME,)


def test_display_name_is_jmxs() -> None:
    assert branding.PRODUCT_NAME == "JMXS"


def test_persistent_identity_does_not_follow_the_display_name(monkeypatch) -> None:
    # Derivation, not coincidence: read the module source with a different
    # display name and every frozen value must come out unchanged.
    source = branding.__spec__.loader.get_source(branding.__name__)
    assert source.count('PRODUCT_NAME = "JMXS"') == 1
    monkeypatch.delenv(branding.OFFICIAL_REPO_SLUG_ENV_VAR, raising=False)
    namespace: dict[str, object] = {"__name__": "branding_renamed"}
    renamed = source.replace('PRODUCT_NAME = "JMXS"', 'PRODUCT_NAME = "Renamed Again"')
    exec(compile(renamed, "branding_renamed", "exec"), namespace)  # noqa: S102
    assert namespace["PRODUCT_NAME"] == "Renamed Again"
    assert {name: namespace[name] for name in _CURRENT_IDENTITY} == _CURRENT_IDENTITY


def test_official_repo_slug_override_is_exact() -> None:
    assert (
        branding.resolve_official_repo_slug({"JMXS_OFFICIAL_REPO_SLUG": "RenamedOrg/RenamedRepo"})
        == "RenamedOrg/RenamedRepo"
    )


def test_the_upstream_override_variable_is_ignored() -> None:
    # A Dodaios environment variable must not redirect JMXS updates.
    assert (
        branding.resolve_official_repo_slug({"JARVIS_OFFICIAL_REPO_SLUG": "Dodaios/Dodaios"})
        == branding.DEFAULT_OFFICIAL_REPO_SLUG
    )


@pytest.mark.parametrize(
    "value",
    [
        "owner",
        "owner/repo/extra",
        "/repo",
        "owner/",
        "owner/repo evil",
        " owner/repo",
        "owner/repo ",
    ],
)
def test_official_repo_slug_override_rejects_non_exact_values(value: str) -> None:
    with pytest.raises(ValueError, match="exact owner/repository slug"):
        branding.resolve_official_repo_slug({"JMXS_OFFICIAL_REPO_SLUG": value})
