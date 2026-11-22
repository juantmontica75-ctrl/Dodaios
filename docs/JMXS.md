# JMXS

JMXS is an independent fork of [Dodaios](https://github.com/Dodaios/Dodaios) (MIT). It keeps the
upstream credits, `LICENSE`, `NOTICE` and original art, and changes the public identity:

| Thing | JMXS |
|---|---|
| Commands | `jmxs`, `jmxsctl`, `jmxs-gateway` |
| Config file | `jmxs.toml` |
| Install folder | `~/.jmxs` |
| Credential service (keyring) | `jmxs` |
| Windows / macOS / Linux names | `JMXS`, `JMXS.app`, `jmxs.desktop` |
| Python import package | `dodaios` (kept on purpose, internal) |

A Dodaios (or Personal Jarvis) installation on the same machine is never migrated, overwritten or
uninstalled by JMXS.

## Install

From source (works on every OS with Python 3.11-3.14 and [uv](https://docs.astral.sh/uv/)):

```bash
git clone https://github.com/juantmontica75-ctrl/Dodaios.git jmxs
cd jmxs
git checkout jmxs/independent-runtime      # until it is merged into main
uv sync
uv run jmxs --version                      # prints: jmxs 5.6.0
```

From a wheel (`uv build --wheel`, includes the web UI):

```bash
python -m venv .venv && . .venv/bin/activate
pip install dist/jmxs-5.6.0-py3-none-any.whl
jmxs --version
```

The one-line installers (`install/install.sh`, `install/install.ps1`) install from this fork once the
branch is on `main`. Never use the upstream Dodaios one-liners for JMXS.

## OmniRoute as a provider

OmniRoute is a gateway you host yourself (OpenAI-compatible). JMXS discovers its models from
`GET /v1/models`; there is no static model list.

```bash
jmxs-gateway url http://localhost:20128/v1
jmxs-gateway key              # paste the key from the OmniRoute dashboard (stdin/prompt, never argv)
jmxs-gateway models
jmxs-gateway select <model-id> --primary
jmxs-gateway show             # url, selected model, key present/missing
```

The key is stored in the OS credential store (slot `omniroute_api_key`) or read from the
`OMNIROUTE_API_KEY` environment variable. `jmxs-gateway forget-key` removes it.

## Maintainers

- Internal namespace stays `dodaios`; change only public identity.
- Windows installer `AppGuid` is JMXS-specific (`packaging/windows/Dodaios.iss`); never reuse the
  upstream one.
- JMXS releases are **not code-signed** and carry no upstream cosign/SLSA identity; the verified
  installer path (`install-verify.*`) pins upstream signing keys and does not apply to JMXS yet.
- See `docs/JMXS-CONTINUITY.md` for the exact state and the verification checklist.
