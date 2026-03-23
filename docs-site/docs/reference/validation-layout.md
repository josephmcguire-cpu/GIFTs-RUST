---
sidebar_position: 2
title: validation directory layout
---

# `validation/` layout and operations

The **`validation/`** tree is a **sibling** of `gifts/` (not a Python package dependency). It hosts the **IWXXM XML** checker: Python orchestration, **CRUX** (Java), cached **OGC/WMO/AIXM** schema trees, and versioned **XML Schema + Schematron** for IWXXM.

Authoritative operational detail: [validation/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/validation/README.md).

## Major paths

| Path | Role |
|------|------|
| [`iwxxmValidator.py`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/validation/iwxxmValidator.py) | CLI entrypoint: build catalog, invoke CRUX, optional GML checks |
| `bin/crux-1.3-all.jar` | CRUX executable (schema + Schematron validation) |
| `catalog.template.xml` | Template for generated OASIS catalog files |
| `schemas/<version>/` | IWXXM XSDs for the chosen `-v` / `--version` (e.g. `2023-1`) |
| `schematrons/<version>/iwxxm.sch` | Schematron rules paired with that version |
| `externalSchemas/` | Local mirror of external OGC/WMO/AIXM dependencies — **may be refreshed**; do not treat as dead bulk |
| `checkGMLReferences.py` | Optional GML / link validation |
| `codeListsToSchematron.py` | Used on **`-f` / `--fetch`** paths and related downloads |

## Working directory

Run **`iwxxmValidator.py`** with **current working directory** set to **`validation/`** so paths to `bin/`, `externalSchemas/`, templates, and generated catalogs resolve as documented.

## Refresh / fetch

**`-f` / `--fetch`** triggers downloads and tooling described in the validation README (including code-list / Schematron refresh). The **`externalSchemas/`** tree is a **cache**; first run or version switches may need network access.

## See also

- [Validation workflow](../workflows/validation) — step-by-step and CLI flags
- [Dependency graphs](../architecture/dependency-graphs) — validator stack diagram
- [E2E workflow](../workflows/e2e) — encode → XML on disk → this validator
