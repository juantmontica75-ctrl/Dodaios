"""The release builds ``jmxs`` only.

The compatibility-package generator stays in the script, switched off for
JMXS (``PUBLISH_COMPAT``); its tests below exercise it with upstream's names.
"""

from __future__ import annotations

import importlib.util
import sys
import tomllib
import types
from pathlib import Path

import pytest
import yaml

from dodaios.core import branding
from scripts.ci import build_distributions as bd

ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_the_names_are_the_distribution_names_branding_declares() -> None:
    assert bd.CURRENT == branding.DISTRIBUTION_NAME
    assert branding.LEGACY_DISTRIBUTION_NAMES == ()
    assert bd.PUBLISH_COMPAT is False


def test_build_setuptools_floor_and_lock_clear_the_advisory() -> None:
    project = tomllib.loads(PYPROJECT)
    requirement = next(
        item for item in project["build-system"]["requires"] if item.startswith("setuptools")
    )
    assert requirement == "setuptools>=84.1.0"

    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    version = next(
        package["version"] for package in lock["package"] if package["name"] == "setuptools"
    )
    assert tuple(int(part) for part in version.split(".")) >= (84, 1, 0)


def _real_project() -> dict:
    return tomllib.loads(PYPROJECT)["project"]


_UPSTREAM = "dodaios"


def _upstream_project() -> dict:
    """The real project table under upstream's name, for the dormant generator."""
    project = _real_project()
    scripts = {"dodaios": "dodaios.__main__:main", "jarvis": "dodaios.__main__:main",
               "personal-jarvis": "dodaios.__main__:main", "jarvisctl": "dodaios.cli_ctl:main"}
    return {**project, "name": _UPSTREAM, "scripts": scripts}


def test_the_earlier_name_is_a_thin_package_pinned_to_the_same_release() -> None:
    project = _upstream_project()
    compat = tomllib.loads(bd.compat_pyproject(project, current=_UPSTREAM))["project"]
    version = project["version"]
    assert compat["name"] == "personal-jarvis"
    assert compat["version"] == version
    # No second copy of the code: one dependency, the current distribution.
    assert compat["dependencies"] == [f"dodaios=={version}"]
    assert compat["requires-python"] == project["requires-python"]
    # Every extra maps to the same extra of the current distribution.
    assert compat["optional-dependencies"] == {
        extra: [f"dodaios[{extra}]=={version}"] for extra in project["optional-dependencies"]
    }
    assert "Dodaios" in compat["description"]


def test_every_command_of_dodaios_keeps_working_under_the_earlier_name() -> None:
    project = _upstream_project()
    compat = tomllib.loads(bd.compat_pyproject(project, current=_UPSTREAM))
    # `uv tool install personal-jarvis` only links the named package's commands.
    assert set(compat["project"]["scripts"]) == set(project["scripts"])
    assert {"jarvis", "personal-jarvis", "dodaios"} <= set(compat["project"]["scripts"])
    assert set(compat["project"]["scripts"].values()) == {f"{bd.COMPAT_MODULE}:main"}
    assert compat["tool"]["setuptools"]["py-modules"] == [bd.COMPAT_MODULE]
    assert project["scripts"]["jarvis"] == "dodaios.__main__:main"
    assert project["scripts"]["personal-jarvis"] == "dodaios.__main__:main"


def test_a_pyproject_under_another_name_is_refused() -> None:
    with pytest.raises(ValueError, match="expected"):
        bd.compat_pyproject({"name": "something-else", "version": "1.0.0"})


def _load_launcher(tmp_path: Path, monkeypatch, project: dict):
    source = bd.compat_module(project, current=_UPSTREAM)
    path = tmp_path / f"{bd.COMPAT_MODULE}.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(bd.COMPAT_MODULE, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_launcher_starts_the_entry_point_of_the_command_it_was_run_as(
    tmp_path: Path, monkeypatch
) -> None:
    project = _upstream_project()
    launcher = _load_launcher(tmp_path, monkeypatch, project)
    assert launcher.command_name(r"C:\venv\Scripts\JarvisCtl.exe") == "jarvisctl"
    assert launcher.command_name("/venv/bin/personal-jarvis") == "personal-jarvis"
    assert launcher.command_name("jarvis-script.py") == "jarvis"

    fake = types.ModuleType("fake_cli")
    fake.main = lambda: "started"
    monkeypatch.setitem(sys.modules, "fake_cli", fake)
    monkeypatch.setattr(launcher, "TARGETS", {"jarvisctl": "fake_cli:main"})
    monkeypatch.setattr(sys, "argv", ["/venv/bin/jarvisctl"])
    assert launcher.main() == "started"
    # Unknown spellings fall back to the main command.
    assert launcher.DEFAULT_TARGET == project["scripts"]["dodaios"]


def test_the_launcher_names_the_repair_when_pip_removed_the_package(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    launcher = _load_launcher(tmp_path, monkeypatch, _upstream_project())

    def missing(name):
        raise ModuleNotFoundError(f"No module named {name!r}", name="dodaios")

    monkeypatch.setattr(launcher, "import_module", missing)
    monkeypatch.setattr(sys, "argv", ["jarvis"])
    assert launcher.main() == 1
    err = capsys.readouterr().err
    version = _real_project()["version"]
    assert f"-m pip install --force-reinstall --no-deps dodaios=={version}" in err


def test_the_launcher_does_not_hide_other_missing_modules(tmp_path: Path, monkeypatch) -> None:
    launcher = _load_launcher(tmp_path, monkeypatch, _upstream_project())

    def missing(name):
        raise ModuleNotFoundError("No module named 'httpx'", name="httpx")

    monkeypatch.setattr(launcher, "import_module", missing)
    with pytest.raises(ModuleNotFoundError):
        launcher.main()


def test_the_readme_says_where_the_project_went() -> None:
    project = _upstream_project()
    readme = bd.compat_readme(project, current=_UPSTREAM)
    assert readme.startswith("# personal-jarvis is now dodaios")
    assert "pip install dodaios" in readme
    assert f"--force-reinstall --no-deps dodaios=={project['version']}" in readme


def _project(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "jmxs"\n'
        'version = "1.2.3"\n'
        'requires-python = ">=3.11"\n'
        'license = "Apache-2.0"\n'
        "[project.scripts]\n"
        'jmxs = "dodaios.__main__:main"\n'
        "[project.optional-dependencies]\n"
        'full = ["jmxs[desktop]"]\n',
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text("license text", encoding="utf-8")
    return tmp_path


def _fake_build(seen: list[tuple[str, str]]):
    def runner(command, cwd: Path) -> None:
        outdir = Path(command[command.index("--outdir") + 1])
        name = tomllib.loads((cwd / "pyproject.toml").read_text(encoding="utf-8"))["project"][
            "name"
        ]
        seen.append((name, outdir.name))
        outdir.mkdir(parents=True)
        for artifact in bd.expected_artifacts(name, "1.2.3"):
            (outdir / artifact).write_bytes(b"artifact")
        # What setuptools leaves behind in the tree.
        (cwd / f"{bd._normalized(name)}.egg-info").mkdir()
        (cwd / "build" / "lib").mkdir(parents=True, exist_ok=True)

    return runner


def test_build_all_builds_jmxs_only_and_leaves_the_tree_as_it_was(tmp_path: Path) -> None:
    root = _project(tmp_path / "tree")
    original = (root / "pyproject.toml").read_bytes()
    (root / "build" / "Jarvis").mkdir(parents=True)  # a PyInstaller freeze
    seen: list[tuple[str, str]] = []

    outputs = bd.build_all(tmp_path / "dist", root=root, runner=_fake_build(seen))

    assert seen == [("jmxs", "jmxs")]
    assert list(outputs) == ["jmxs"]
    assert sorted(p.name for p in outputs["jmxs"].iterdir()) == [
        "jmxs-1.2.3-py3-none-any.whl",
        "jmxs-1.2.3.tar.gz",
    ]
    assert not (tmp_path / "dist" / "personal-jarvis").exists()
    assert (root / "pyproject.toml").read_bytes() == original
    assert not list(root.glob("*.egg-info"))
    assert not (root / "build" / "lib").exists()
    assert (root / "build" / "Jarvis").is_dir()


def test_a_tree_under_another_name_is_refused(tmp_path: Path) -> None:
    root = _project(tmp_path / "tree")
    pyproject = root / "pyproject.toml"
    pyproject.write_text(pyproject.read_text().replace('"jmxs"', '"dodaios"', 1))
    with pytest.raises(ValueError, match="expected 'jmxs'"):
        bd.build_all(tmp_path / "dist", root=root, runner=_fake_build([]))


def test_a_missing_artifact_fails_the_build(tmp_path: Path) -> None:
    root = _project(tmp_path / "tree")

    def runner(command, cwd: Path) -> None:
        Path(command[command.index("--outdir") + 1]).mkdir(parents=True)

    with pytest.raises(ValueError, match="expected"):
        bd.build_all(tmp_path / "dist", root=root, runner=runner)


def _release() -> dict:
    return yaml.safe_load((ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"))


def test_the_release_builds_and_publishes_jmxs_only() -> None:
    jobs = _release()["jobs"]
    build_runs = "\n".join(step.get("run", "") for step in jobs["build"]["steps"])
    assert "scripts/ci/build_distributions.py --outdir dist" in build_runs
    assert "python -m build " not in build_runs
    assert "publish-legacy" not in jobs
    uploads = [
        step["with"]["packages-dir"]
        for step in jobs["publish"]["steps"]
        if "gh-action-pypi-publish@" in step.get("uses", "")
    ]
    assert jobs["publish"]["environment"] == "pypi"
    assert uploads == ["dist/jmxs/"]
    assert jobs["publish"]["permissions"] == {"id-token": "write"}
