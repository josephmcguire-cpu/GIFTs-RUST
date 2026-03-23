---
sidebar_position: 3
title: Use cases
---

# Use cases

Each row links to a **workflow** (operational steps) and **architecture** (modules and diagrams).

| ID | Actor | Goal | Preconditions | Primary path | Workflows | Architecture |
|----|-------|------|---------------|--------------|-----------|--------------|
| UC-1 | Developer / service | Encode **METAR/SPECI** (and similar) TAC to IWXXM | AHL + TAC; geo DB for METAR/TAF | `Encoder.encode` → `Bulletin` → `write()` | [Library encode](./workflows/library-encode), [METAR pipeline](./architecture/metar-pipeline) | [gifts modules](./architecture/gifts-modules) |
| UC-2 | Operator | **Interactive** conversion via GUI | Tk; pickle aerodrome DB in `demo/` | File pick → match AHL → encode → log + bulletin file | [Demo GUI](./workflows/demo-gui) | [Demo modules](./architecture/demo-modules) |
| UC-3 | Operator / batch job | **Watch folder** and emit IWXXM files | `watchdog`; cfg dirs exist | `iwxxmd.py` + `.cfg` | [iwxxmd daemon](./workflows/iwxxmd-daemon) | [Demo modules](./architecture/demo-modules) |
| UC-4 | QA / integrator | **Validate** IWXXM XML on disk | Java + CRUX + schemas | `iwxxmValidator.py <dir>` | [Validation](./workflows/validation) | [Validation modules](./architecture/validation-modules) |
| UC-5 | Maintainer | **Regression**: stable TAC→XML vs goldens | pytest; `testdata/pipeline` | Harness mocks time/UUID; compare XML | [Pipeline goldens](./workflows/pipeline-goldens) | [Overview](./architecture/overview) |

## Typical METAR→IWXXM path (summary)

1. Provide a string with **WMO AHL** matching METAR/SPECI and one or more **METAR/SPECI** TAC bodies.
2. Construct `gifts.METAR.Encoder(geoLocationsDB)`.
3. Call `encode(text)` → receive `Bulletin` with IWXXM elements.
4. Call `bulletin.write()` (optionally `compress=True`).

See [METAR pipeline](./architecture/metar-pipeline) for decode→encode internals.
