---
sidebar_position: 8
title: Python package
---

# Python package (`gifts`)

The installable distribution is defined in [`pyproject.toml`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/pyproject.toml).

| Field | Value (check repo for current) |
|-------|--------------------------------|
| Name | `gifts` |
| `requires-python` | `>=3.9` |
| Runtime deps | `skyfield` (see `[project] dependencies`) |
| Optional **`[test]`** | `pytest`, `pytest-cov`, `pytest-benchmark`, `freezegun`, `ruff`, `lxml`, `requests`, `watchdog` |
| Package data | RDF under `gifts/data/` via `[tool.setuptools.package-data]` |

## Editable install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
```

## Wheels and sdist

From the repo root:

```bash
make build
# or: python -m build
```

Uses `setuptools` backend per `pyproject.toml`.

## What is not packaged

`demo/`, `validation/`, `tests/`, `testdata/`, `docs-site/` are **not** part of the `gifts` wheel; they ship with the **repository** for tooling and docs.
