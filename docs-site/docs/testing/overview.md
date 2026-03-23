---
sidebar_position: 1
title: Testing overview
---

# Testing overview

Pytest layout, markers, coverage gates, and Makefile targets. See [tests/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/tests/README.md).

## Test trees

| Path | Scope |
|------|--------|
| `gifts/tests/` | `gifts` package unit/integration |
| `validation/tests/` | `validation/*.py` (GML, code lists, validator wiring) |
| `demo/tests/` | `demo1.py`, `iwxxmd.py` paths and behavior |
| `tests/pipeline/` | Frozen TAC→IWXXM vs `testdata/pipeline` goldens |
| `tests/e2e/` | Encode → XML on disk → `iwxxmValidator` (skips without Java/schemas) |
| `tests/perf/` | `pytest-benchmark` (not run in default `make test`) |

## Markers

| Marker | Meaning |
|--------|---------|
| `e2e` | Cross-service e2e (see [E2E workflow](../workflows/e2e)) |
| `integration` | Optional CRUX / validator in pipeline tests |
| `perf` | Benchmark suite |
| `gui` / `daemon` / `requires_docker` | Used where tests need Tk, long runs, or Docker |

## Coverage and Makefile

- **`make test`** — all of the above except `perf` (`-m "not perf"`).
- **`make test-cov`** — same tests with HTML coverage for `gifts`, `demo`, `validation` Python.
- **Per-tree gates** — `make test-gifts`, `test-validation`, `test-demo` match CI **≥99%** line coverage on each tree (see [TRD](../trd)).

## Repo-wide pytest config

[`conftest.py`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/conftest.py) at the repository root applies **`pytest_configure`** warning filters (e.g. urllib3/LibreSSL, NumPy reload) so noisy environment warnings do not fail strict test runs.

## See also

- [Pipeline goldens](./pipeline-goldens)
- [CI workflows](../reference/ci-workflows)
- [Dependency graphs](../architecture/dependency-graphs)
