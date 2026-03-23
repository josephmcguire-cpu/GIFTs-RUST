---
sidebar_position: 2
title: Technical requirements
---

# Technical requirements

Summary of runtime, tooling, and quality expectations for the GIFTs monorepo. Authoritative detail remains in the linked READMEs and `pyproject.toml`.

## Purpose and scope

- **In scope**: Python library `gifts` (TAC to IWXXM), `demo` utilities (GUI + file-watcher daemon), `validation` helpers (IWXXM XML validation via CRUX), and cross-repo tests under `tests/` and `testdata/`.
- **Out of scope for the library**: HTTP APIs; dissemination beyond producing XML and optional `MeteorologicalBulletin` packaging (see root README).

## Runtime

| Requirement | Notes |
|-------------|--------|
| Python | **≥ 3.9** (`requires-python` in `pyproject.toml`) |
| Java | On `PATH` for `validation/iwxxmValidator.py` (invokes CRUX JAR under `validation/bin/`) |
| Tk | Optional; required only for `demo/demo1.py` GUI |

## Python dependencies

| Area | Packages | Source |
|------|-----------|--------|
| Library runtime | `skyfield` | `pyproject.toml` `dependencies` |
| Editable dev / tests | `pytest`, `pytest-cov`, `pytest-benchmark`, `freezegun`, `ruff`, `lxml`, `requests`, `watchdog` | `[project.optional-dependencies] test` |
| Demo daemon | `watchdog` | `iwxxmd.py` |

## Validation stack

- Run `iwxxmValidator.py` from the **`validation/`** directory (see script preamble): expects `bin/crux-1.3-all.jar` and `externalSchemas/` relative to that working directory.
- IWXXM **schema + Schematron** paths use `-v` / `--version` (default in argparse is `2023-1`; align with site output — see `gifts/common/xmlConfig.py` and `IWXXM_VALIDATOR_VERSION`).
- Optional **GML** reference checks via `checkGMLReferences.py` unless `--noGMLChecks`.

## Inputs and outputs

| Artifact | Contract |
|----------|-----------|
| TAC message | One **WMO AHL** line appropriate to embedded TAC; METAR/SPECI/TAF bodies from keyword through `=`; advisories typically one per file (`demo/README`) |
| METAR/TAF encoders | **ICAO → location** map (`geoLocationsDB` with `.get(icao, default)`); pickle workflow in `gifts/database/README` |
| Encoder output | `gifts.common.bulletin.Bulletin` of IWXXM `Element` roots; `write()` emits `MeteorologicalBulletin`; `compress=True` for gzip (root README) |

## Quality and CI

- **Lint**: Ruff on agreed trees (`Makefile` `lint`, `.github/workflows/lint.yml`).
- **Coverage gates**: ≥99% line coverage per Python tree for `gifts/`, `validation/*.py`, `demo/*.py` (see `Makefile` and `test-*.yml` workflows).
- **Tests**: `gifts/tests`, `validation/tests`, `demo/tests`, `tests/pipeline`, `tests/e2e`, `tests/perf` (see `tests/README.md`).
- **Docs index**: [CI workflows](./reference/ci-workflows), [Testing overview](./testing/overview), [Pipeline goldens](./testing/pipeline-goldens), [E2E workflow](./workflows/e2e).

## Packaging and operations

- [Python package](./reference/python-package) — `pyproject.toml`, editable install, wheels.
- [Docker](./reference/docker) — `Dockerfile.gifts`, `Dockerfile.validation`, `Dockerfile.demo`, Compose services and **`e2e`** profile.

## Repository map

- [Repository layout](./reference/repository-layout) — top-level trees (`gifts/`, `validation/`, `demo/`, `tests/`, `testdata/`, `tools/`, `docs-site/`, workflows).
- [Dependency graphs](./architecture/dependency-graphs) — how library, validation, CI, and artifacts relate.

## Documentation site (this folder)

- Built with **Docusaurus 3** under `docs-site/`; requires **Node ≥ 18** for local preview and CI build.
- Contributor expectations: [Contributing](./contributing).
