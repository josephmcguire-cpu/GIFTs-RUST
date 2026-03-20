# pyproject.toml — reference sketch

Modern uv-centric projects center on **`[project]`**, **`[dependency-groups]`** (PEP 735), and tool tables under **`[tool.*]`**.

## Build backend

Prefer **`uv_build`** for simple packages when starting fresh (aligns with Astral/uv defaults in many templates). Use **hatchling** or others only when the project needs their features.

```toml
[build-system]
requires = ["uv_build>=0.8.0,<0.9.0"]
build-backend = "uv_build"
```

(Exact version bounds: follow uv release notes / template you use.)

## Project metadata

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "..."
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
mycli = "myproject.cli:main"
```

## Dependency groups (dev tools)

Use **`[dependency-groups]`** for linters, testers, docs—not `[project.optional-dependencies]` for dev-only stacks.

```toml
[dependency-groups]
dev = [{include-group = "lint"}, {include-group = "test"}]
lint = ["ruff", "ty"]
test = ["pytest", "pytest-cov"]
```

Install with `uv sync --all-groups` or selective `--group`.

## Ruff

See [ruff-config.md](ruff-config.md). Minimum useful split:

- `[tool.ruff]` — line length, target Python
- `[tool.ruff.lint]` — `select` / `ignore`
- `[tool.ruff.format]` — if customizing formatter

## ty

Put **Python version** under **`[tool.ty.environment]`**, not a stray key under `[tool.ty]`:

```toml
[tool.ty.environment]
python-version = "3.11"

[tool.ty.terminal]
error-on-warning = true
```

## pytest

```toml
[tool.pytest.ini_options]
addopts = ["--strict-markers", "--cov=myproject", "--cov-fail-under=80"]
testpaths = ["tests"]
```

Package name in `--cov=` must match the import name.

## Coverage (optional)

Often via `pytest-cov` addopts; standalone `coverage.toml` is fine for larger projects—see [testing.md](testing.md).
