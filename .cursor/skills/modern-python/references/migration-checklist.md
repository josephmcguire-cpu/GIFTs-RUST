# Migration cleanup checklist

Use after moving a project to **uv** + **pyproject.toml**.

## Files to remove (when superseded)

- [ ] `requirements.txt`, `requirements-*.txt` (deps now in `pyproject.toml` / `uv.lock`)
- [ ] `setup.py`, `setup.cfg`, `MANIFEST.in` (if fully migrated to PEP 621 metadata)
- [ ] Legacy venv dirs: `venv/`, `.venv/` (uv creates its own; do not commit)
- [ ] Tool configs: `.flake8`, `mypy.ini`, `pyrightconfig.json`, `.isort.cfg` (if replaced by ruff/ty)

## Files to add / keep

- [ ] `uv.lock` **committed** for applications and reproducible builds
- [ ] `.python-version` (optional but recommended for teams)
- [ ] `pyproject.toml` as single source of truth

## Verification

- [ ] `uv sync --all-groups` succeeds on a clean clone
- [ ] `uv run pytest` (or project test command) passes
- [ ] `uv run ruff check .` and `uv run ruff format --check` clean
- [ ] `uv run ty check src/` (adjust path to package) clean or baseline documented

## CI

- [ ] Workflows install via **`uv`** (official action or `curl` installer) and run **`uv sync`** before tests
- [ ] Pin **Python version** to match `requires-python` / `tool.ty.environment`
