# JMXS continuity log

JMXS is an independent fork of Dodaios. This file records the state of the
work so any session can resume exactly where the previous one stopped.

## Repository

- Fork: `juantmontica75-ctrl/Dodaios`
- Base: `main` at `734d8c4` (identical to upstream at fork time)
- Working branch: `jmxs/independent-runtime` (local only, not pushed)
- Workspace path: `/vercel/share/projects/github-1467628561`

## History

- Session 1 (Astra): changed branding, update contract, packaging, added an
  OmniRoute provider and `jmxs-gateway`, 39 unit tests passed, built
  `jmxs-5.6.0-py3-none-any.whl`. None of it was committed or pushed; the
  workspace was lost. The remote has no `jmxs/independent-runtime` branch.
- Session 2: re-cloned the fork, recreated `jmxs/independent-runtime` from
  `734d8c4`, added this log. Waiting for the user's copy of Astra's files
  so the real implementation is restored instead of reinvented.

## Phases

| # | Phase | Status |
|---|-------|--------|
| 0 | Branch + continuity log | done |
| 1 | Restore Astra's files from the user's copy and diff against `main` | blocked: files not yet provided |
| 2 | Identity (`branding.py`, update contract, rollback, `pyproject.toml`, `uv.lock`) | pending |
| 3 | Frontend branding (`branding.ts`, tests, `index.html`) | pending |
| 4 | OmniRoute provider + `jmxs-gateway` CLI + tests | pending |
| 5 | Native packaging (`dodaios.spec`, PyInstaller runtime hook) | pending |
| 6 | Validation: unit tests, frontend build, wheel contents, clean install | pending |

## Files expected from Astra's copy

```
README.md
docs/JMXS.md
dodaios.spec
dodaios/__main__.py
dodaios/brain/manager.py
dodaios/core/branding.py
dodaios/core/update_contract.py
dodaios/missions/init.py
dodaios/missions/workers/api_agent_worker.py
dodaios/setup/update_rollback.py
dodaios/plugins/brain/omniroute.py
dodaios/plugins/brain/omniroute_cli.py
dodaios/ui/web/frontend/index.html
dodaios/ui/web/frontend/src/lib/branding.ts
dodaios/ui/web/frontend/src/lib/branding.test.ts
install/update-contract.json
packaging/pyinstaller_rthook_frozen.py
pyproject.toml
uv.lock
tests/unit/core/test_branding.py
tests/unit/brain/test_jmxs_omniroute.py
```

## Rules

- Commit locally after every phase. No push, publish or deploy without the
  user's explicit approval.
- Keep the internal `dodaios` Python namespace; change only public identity.
- Do not migrate Dodaios keychains, configs, install markers, mutexes or
  update origins.
- Keep original art, credits, NOTICE and LICENSE.

## Next task

Receive Astra's files, copy them over the branch, review `git diff main`,
then run the Phase 6 checks.
