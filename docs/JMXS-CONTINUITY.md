# JMXS continuity log

JMXS is an independent fork of Dodaios. This file records the state of the
work so any session can resume exactly where the previous one stopped.
Read it first, then run `git log --oneline main..HEAD`.

## Repository

- Fork: `juantmontica75-ctrl/Dodaios`
- Base: `main` at `734d8c4` (identical to upstream at fork time)
- Working branch: `jmxs/independent-runtime`
- Workspace path used: `/vercel/share/projects/github-1467628561`
- Python env: `.venv` (Python 3.13, created with `uv sync`); test deps
  installed with `uv pip install --python .venv/bin/python pytest pytest-asyncio pytest-timeout`

## History

- Session 1 (Astra): work lost, never committed or pushed. Its files were not
  recoverable; everything below was rebuilt from the handoff document.
- Session 2: recreated the branch from `734d8c4` and rebuilt the work.

## Commits on the branch (oldest first)

1. `ead8f5f` docs: continuity log.
2. `54bff6e` feat(brain): OmniRoute provider + `jmxs-gateway` CLI. Complete.
3. WIP commit: JMXS independent identity (see "Identity" below). Incomplete.
4. This log update.

## OmniRoute (complete, tested)

- `dodaios/plugins/brain/omniroute.py`: OpenAI-compatible brain plugin.
  Default base URL `http://localhost:20128/v1` (OmniRoute's default port).
  Key: config secret slot `omniroute_api_key` or env `OMNIROUTE_API_KEY`.
  Models discovered via `GET /v1/models`.
- `dodaios/plugins/brain/omniroute_cli.py`: `jmxs-gateway` command with
  `url`, `key` (stdin/prompt only, never argv), `forget-key`, `models`,
  `select [--primary]`, `clear-selection`, `show`.
- Wired into: `core/config.py` secrets, `brain/manager.py`,
  `brain/model_catalog.py`, `brain/app_control.py`,
  `brain/voice_command_gate.py`, `ui/web/provider_spec.py`,
  `ui/web/provider_families.py`, `agent_chat/{catalog,effort,runner_api}.py`,
  `missions/init.py`, `missions/workers/api_agent_worker.py`,
  `missions/worker_runtime/provider_map.py`, `missions/critic/runner.py`,
  `missions/voice/readback.py`, `setup/wizard.py`, `pyproject.toml`
  (entry points `omniroute` brain + `jmxs-gateway` script).
- Tests: `tests/unit/brain/test_omniroute_provider.py` — 29/29 pass.

How a user connects OmniRoute once installed:

```bash
jmxs-gateway url http://localhost:20128/v1
jmxs-gateway key            # paste the key from the OmniRoute dashboard
jmxs-gateway models
jmxs-gateway select <model-id> --primary
jmxs-gateway show
```

## Identity (mostly done)

Done and committed (see `git log` on this branch):
- `6cba3f2` branding tests frozen for JMXS. The slug validation was never
  lost: tests used the upstream `JARVIS_OFFICIAL_REPO_SLUG`; JMXS reads
  `JMXS_OFFICIAL_REPO_SLUG`. Every install-reaching `LEGACY_*` tuple is empty.
  Web title is JMXS.
- `564f50f` relock for dist `jmxs`; `desktop`/`full` extras now name
  `jmxs[...]` (they pulled the upstream Dodaios wheel before).
- `a572c2b` frozen app identity: JMXSApp/jmxs, `JMXS.app`, own bundle id,
  `JMXS` data dir, `jmxs.toml`, JMXS mutexes. No earlier names adopted.
- `3a80501` release CI builds/publishes `jmxs` only (`PUBLISH_COMPAT` off).
- `97a44f9` uninstallers remove JMXS only; earlier names are aliases of the
  current ones (never empty, an empty name resolves to `$HOME`).

## Test suite status

- Baseline on `main`: 9 failures (pre-existing, not ours).
- On this branch roughly 200 extra failures came from tests that index
  `LEGACY_*[0]` (now empty) or assert Dodaios/Jarvis values.
- WIP commit "test: skip earlier-name adoption tests" adds a
  `_NEEDS_EARLIER_NAMES` skipif to modules that only test migrating an
  earlier product name, and guards `LEGACY_*[0]` with `(X or ("",))[0]`.
  Running those 10 modules: 20 pass, 29 skip, 17 FAIL. The 17 failures
  (`tests/unit/autostart/test_linux.py`,
  `tests/unit/setup/test_desktop_integration.py`) assert current values
  like `dodaios.desktop` — update them to the JMXS values, do NOT skip.
- Handle BY HAND (a blanket skip hid real coverage, reverted):
  `tests/unit/autostart/test_windows_task.py` (31 tests share
  `_LEGACY_TASK_NAME` through a fake schtasks helper) and
  `tests/unit/setup/test_uninstall.py` (module-level `MARKER` from
  `LEGACY_KEYRING_SERVICES[0]`). Skip only the legacy-specific tests,
  keep the rest running against the current names.

## Pending, in order

1. Fix the 17 failures above; hand-edit `test_windows_task.py` and
   `test_uninstall.py`.
2. Run the full unit suite and compare against the 9-failure baseline
   (`uv run pytest tests/unit -q -x` is slow: ~8 min+, run per folder).
3. `README.md` JMXS section + `docs/JMXS.md` (install, credits, upstream
   one-line installers must NOT be used for JMXS).
4. `git diff --check`, `python -m compileall -q dodaios`, OmniRoute and
   `tests/unit/brain/test_litellm_provider_wiring.py`, then
   `npm ci && npm test && npm run build` in `dodaios/ui/web/frontend`.
5. `uv build --wheel`, check it contains `dodaios/ui/web/dist/index.html`
   and `dodaios/plugins/brain/omniroute.py`, install in a fresh venv, run
   `jmxs --version` and `jmxs-gateway show`.

## Rules

- Commit after every phase. No push to `main`, no publish or deploy without
  the user's explicit approval.
- All code, comments and commits in English (AGENTS.md).
- Keep the internal `dodaios` Python namespace; change only public identity.
- Do not migrate Dodaios keychains, configs, install markers, mutexes or
  update origins.
- Keep original art, credits, NOTICE and LICENSE.
- Never print or commit secrets (`.env*`, API keys).

## Session 4 (recovery from handoff zip)

Verified state: remote `jmxs/independent-runtime` was at `fee50a2`; the
session-3 commits (`17e4b14` .. `46f0c18`) never reached GitHub and are not
recoverable as diffs. Their intent is being redone on top of `fee50a2`.

Done in this session (local commit, push pending — the sandbox had no GitHub
credential, only the file-level GitHub connector):
- CLI/control-CLI tests rewritten for `jmxs` / `jmxsctl` (no earlier names);
  `jmxsctl version` now prints `PRODUCT_NAME` instead of a hard-coded "Dodaios".
- `tests/unit/core/test_identity_single_source.py`: collection error fixed
  (`_first()` guard), expectations rewritten for empty `LEGACY_*` tuples.
- Real product bugs found by those tests and fixed: STT plugins read keyring
  service `dodaios` (now `jmxs`); OpenRouter plugins sent the upstream
  Referer / `X-Title: Dodaios`; PyInstaller `CFBundleName` was "Dodaios";
  `pyproject.toml` installed docs under `share/dodaios/` while the code reads
  `share/<distribution>/` (now `share/jmxs/`).

STILL OPEN (tests in `test_identity_single_source.py` fail on purpose until done):
1. `packaging/windows/Dodaios.iss`: names, publisher, URL, exe names, and a NEW
   `AppGuid` (JMXS must not upgrade over a Dodaios install). Update the
   SignPath/CI names that pin the setup file name.
2. `packaging/windows/build.ps1`, `packaging/linux/build.sh`,
   `packaging/macos/build.sh`: JMXS names, no `PersonalJarvis`/`jarvis` shims.
3. `install/install.sh`, `install/install.ps1`, `install/install-verify.*`:
   still the Dodaios one-line installers (`.dodaios`, upstream raw URLs).
4. `dodaios/cli/app_update.py` (and `response_style.py`, `voice_engine/models.py`)
   still point at `github.com/Dodaios/Dodaios` installers/URLs.
5. Folder-by-folder main-vs-branch unit comparison after `credential_broker`,
   `brain` file by file; full `npm test`, build with
   `NODE_OPTIONS=--max-old-space-size=4096`, ruff classification, wheel rebuild.
   This sandbox lacks typer/httpx/tomlkit/pytest-asyncio and cannot install
   them, so those runs must happen where dependencies are available.
