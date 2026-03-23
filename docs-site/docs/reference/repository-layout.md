---
sidebar_position: 1
title: Repository layout
---

# Repository layout

Top-level map of the monorepo. Normative operational detail remains in subtree READMEs; this page is a **navigation index**.

| Path | Role | Canonical README |
|------|------|-------------------|
| `gifts/` | Installable **TAC → IWXXM** library (`pip install -e .`) | [Root README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/README.md) |
| `gifts/common/` | `Encoder`, `bulletin`, `xmlConfig`, `xmlUtilities`, shared helpers | — |
| `gifts/database/` | Pickled ICAO → aerodrome metadata for METAR/TAF | [gifts/database/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/gifts/database/README.md) |
| `gifts/data/` | WMO code-registry RDF used by encoders | — |
| `validation/` | **IWXXM XML** validation (Python + Java CRUX), schemas, Schematron, `externalSchemas/` | [validation/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/validation/README.md) |
| `demo/` | `demo1.py` GUI, `iwxxmd.py` daemon, sample TAC files | [demo/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/demo/README.md) |
| `tests/` | Cross-cutting pytest (`pipeline`, `e2e`, `perf`) | [tests/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/tests/README.md) |
| `testdata/` | Frozen pipeline cases + golden XML | [testdata/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/testdata/README.md) |
| `tools/` | Maintainer scripts (e.g. freeze pipeline goldens) | — |
| `scripts/` | Shell helpers (e.g. `docs-with-npm.sh` for Make) | — |
| `docs-site/` | This Docusaurus site | [docs-site README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/docs-site/README.md) |
| `Dockerfile.gifts` / `Dockerfile.validation` / `Dockerfile.demo` | Container images for dev/CI-style runs | [Docker](./docker) |
| `docker-compose.yml` | Local orchestration of those images | [Docker](./docker) |
| `.github/workflows/` | CI: lint, tests, e2e, perf, docker-smoke, docs | [CI workflows](./ci-workflows) |
| `conftest.py` | Repo-root pytest hooks (if any) | [Testing overview](../testing/overview) |

IDE-only paths (e.g. `.cursor/`) are not part of the shipped product; omit from operational docs.

## validation/ subtree (names only)

| Subpath | Purpose |
|---------|---------|
| `bin/` | CRUX JAR |
| `schemas/<version>/` | IWXXM XSD tree for `-v` |
| `schematrons/<version>/` | `iwxxm.sch` and related |
| `externalSchemas/` | Cached OGC/WMO/AIXM mirrors (refresh from upstream; do not treat as dead bulk) |
| `*.py` | `iwxxmValidator.py`, `checkGMLReferences.py`, `codeListsToSchematron.py` |

See [Validation layout](./validation-layout) for dependencies.

## See also

- [Dependency graphs](../architecture/dependency-graphs) — who depends on whom (services, artifacts, modules); good **first** read for the whole repo
- [Repository overview](../architecture/overview) — diagrams and narrative
