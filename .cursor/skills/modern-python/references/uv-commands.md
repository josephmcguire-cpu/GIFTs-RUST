# uv command reference (condensed)

Official source: [Astral uv documentation](https://docs.astral.sh/uv/).

## Project lifecycle

| Command | Purpose |
|---------|---------|
| `uv init [path]` | New project (script or minimal layout) |
| `uv init --package name` | `src/` package layout for distribution |
| `uv init --bare` | Add `pyproject.toml` to existing directory |
| `uv add pkg` | Add runtime dependency (updates pyproject + lock) |
| `uv add --group dev pkg` | Add to dependency group |
| `uv remove pkg` | Remove dependency |
| `uv sync` | Install from lockfile |
| `uv sync --all-groups` | Include all `[dependency-groups]` |
| `uv lock` | Refresh `uv.lock` without installing |

## Execution

| Command | Purpose |
|---------|---------|
| `uv run cmd` | Run in project environment (no manual `activate`) |
| `uv run --with pkg cmd` | Ephemeral extra packages for one command |
| `uv run python -m pytest` | Example: test runner |
| `uvx tool` | Ephemeral tool (like `npx`; e.g. `uvx ruff`) |

## Build / publish

| Command | Purpose |
|---------|---------|
| `uv build` | Build sdist/wheel |
| `uv publish` | Upload to index (configure tokens per CI docs) |

## Scripts (PEP 723)

| Command | Purpose |
|---------|---------|
| `uv run script.py` | Run script; honors inline metadata block |

See [pep723-scripts.md](pep723-scripts.md).
