# Ruff configuration

Ruff replaces **flake8**, **black**, **isort**, **pyupgrade**, and many plugins—configure mostly in **`[tool.ruff]`** and **`[tool.ruff.lint]`**.

## Starting point (strict + pragmatic)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["ALL"]
# Common noise reducers; tune per project:
ignore = [
  "D",       # pydocstyle — opt back in for public APIs
  "COM812",  # trailing comma — can fight black-style format
  "ISC001",  # import sorting single-line — sometimes conflicts with format
]
```

## Fixing vs formatting

- **Lint with autofix**: `uv run ruff check --fix .`
- **Format** (like black): `uv run ruff format .`
- **CI**: `uv run ruff format --check . && uv run ruff check .`

## Per-file ignores

Use for tests, migrations, or generated code:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # assert allowed in tests
```

## Import sorting

Ruff’s isort rules live under the **I** group in `select`; no separate isort config needed.

## Docstring style

If enabling **D** rules, pick a convention (`[tool.ruff.lint.pydocstyle]`)—otherwise keep **D** ignored until the team commits to docstrings.
