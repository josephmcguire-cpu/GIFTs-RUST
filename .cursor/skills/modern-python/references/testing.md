# Testing with pytest + coverage

## Dependencies

Add via uv (typically a `test` group):

```bash
uv add --group test pytest pytest-cov
```

## pyproject snippet

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
  "-ra",
  "--strict-markers",
  "--cov=myproject",
  "--cov-report=term-missing",
  "--cov-fail-under=80",
]
```

Replace `myproject` with the **import package name** under `src/`.

## Layout

- **`src/` layout**: tests live in `tests/`, import the installed package (not `src/` directly).
- Mark optional slow tests with `@pytest.mark.slow` and exclude in default addopts if needed.

## Running

```bash
uv run pytest
uv run pytest tests/test_specific.py -k pattern
```

## Coverage tips

- Fail CI under threshold (`--cov-fail-under`) to prevent silent coverage decay.
- For multi-package repos, use **`coverage run -m pytest`** or configure `[tool.coverage.run]` `source` / `omit` as complexity grows.
