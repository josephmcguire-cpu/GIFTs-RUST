---
sidebar_position: 2
title: Pipeline golden tests
---

# Pipeline golden tests

Regression suite under `tests/pipeline` replays committed **TAC** inputs and compares encoder output to **golden XML** under `testdata/pipeline`. See [testdata README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/testdata/README.md).

## Layout

| Piece | Role |
|-------|------|
| `testdata/pipeline/<case>/input.txt` | TAC (+ AHL) fed to the harness |
| `testdata/pipeline/<case>/case.json` | Metadata (encoder module, xmlConfig overrides, etc.) |
| `testdata/pipeline/<case>/golden/*.xml` | Expected IWXXM fragments or documents |

## Harness behavior

[`golden_harness.py`](https://github.com/josephmcguire/GIFTs-RUST/blob/main/tests/pipeline/golden_harness.py) builds deterministic output by mocking **wall-clock** and **UUID** generation so XML matches committed goldens across runs.

## Regenerating goldens

When encoder output **intentionally** changes, refresh assets from the repo root:

```bash
python tools/freeze_pipeline_cases.py
```

Optional **`--validate`** runs `iwxxmValidator.py` on golden XML when CRUX and schema trees exist locally.

See [`tools/freeze_pipeline_cases.py`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/tools/freeze_pipeline_cases.py) docstring.

## Workflow summary

Also described under [Pipeline goldens workflow](../workflows/pipeline-goldens).
