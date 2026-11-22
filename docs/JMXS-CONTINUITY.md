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

## Identity (work in progress, NOT finished)

Changed so far (WIP commit):
- `dodaios/core/branding.py`: product name JMXS, fork repo slug, JMXS install
  identifiers (Windows/macOS/Linux), no migration aliases from Dodaios/Jarvis.
- `dodaios/core/update_contract.py`, `dodaios/setup/update_rollback.py`:
  fallback to the JMXS name when no legacy names exist.
- `install/update-contract.json`: `jmxs.toml`, `JMXS.app`, `com.jmxs...`.
- `dodaios/ui/web/frontend/src/lib/branding.ts`: JMXS name, fork repo,
  upstream credit constants, MCP server name `jmxs`.
- `pyproject.toml`: dist name `jmxs`, commands `jmxs`, `jmxsctl`,
  `jmxs-review-gc`, `jmxs-review-eval`, `jmxs-gateway`. Import package stays
  `dodaios` on purpose.

Test status: `tests/unit/core/test_branding.py` 15 failed / rest pass.
- 8 failures are expected: the tests still assert Dodaios/Jarvis identity
  values and legacy aliases. Rewrite them for JMXS.
- 7 failures `DID NOT RAISE ValueError` in
  `test_official_repo_slug_override_rejects_non_exact_values`: the rewritten
  `resolve_official_repo_slug` lost its input validation. REAL BUG — restore
  the exact `owner/repo` validation from `git show main:dodaios/core/branding.py`.
- `test_official_repo_slug_override_is_exact`: override env var not honoured
  any more; same function.

## Pending, in order

1. Fix `resolve_official_repo_slug` validation in `dodaios/core/branding.py`.
2. Update `tests/unit/core/test_branding.py` and
   `dodaios/ui/web/frontend/src/lib/branding.test.ts` for JMXS values.
3. `dodaios/ui/web/frontend/index.html` title -> JMXS.
4. `uv lock` (dist renamed to `jmxs`), then `uv sync --locked`.
5. `dodaios.spec` + `packaging/pyinstaller_rthook_frozen.py`: JMXSApp,
   `JMXS.app`, `ai.jmxs.desktop`, data dir `JMXS`, `jmxs.toml`, own mutexes.
6. `README.md` JMXS section + `docs/JMXS.md` (install, credits, upstream
   one-line installers must NOT be used for JMXS).
7. Run: `git diff --check`, `python -m compileall -q dodaios`, the branding,
   OmniRoute and `tests/unit/brain/test_litellm_provider_wiring.py` tests,
   `npm ci && npm test && npm run build` in `dodaios/ui/web/frontend`.
8. `uv build --wheel`, check the wheel contains
   `dodaios/ui/web/dist/index.html` and `dodaios/plugins/brain/omniroute.py`,
   install it in a fresh venv, run `jmxs --version` and `jmxs-gateway show`.

## Rules

- Commit after every phase. No push to `main`, no publish or deploy without
  the user's explicit approval.
- All code, comments and commits in English (AGENTS.md).
- Keep the internal `dodaios` Python namespace; change only public identity.
- Do not migrate Dodaios keychains, configs, install markers, mutexes or
  update origins.
- Keep original art, credits, NOTICE and LICENSE.
- Never print or commit secrets (`.env*`, API keys).
