---
sidebar_position: 14
title: Pipeline golden tests
---

# Pipeline golden test workflow

`tests/pipeline` replays committed **TAC** inputs under `testdata/pipeline/<case>/`, runs the same encode path with **deterministic** time and UUID mocks, and compares XML (and optional stages) to **golden** files.

## Flow

```mermaid
flowchart TD
  case[testdata_pipeline_case]
  json[case_json_metadata]
  inp[input_txt_TAC]
  harness[golden_harness]
  mock[fixed_clock_and_UUID]
  enc[product_Encoder]
  gold[golden_xml_on_disk]
  diff[compare_or_update]

  case --> json
  case --> inp
  harness --> mock
  inp --> enc
  mock --> enc
  enc --> diff
  gold --> diff
```

## Maintainer notes

- Regenerate goldens with the repository tooling when encoders intentionally change (`tools/freeze_pipeline_cases.py`; see `testdata/README.md`).
- Some tests may invoke **`iwxxmValidator.py`** when Java and schema trees are present (integration marker).

## Related docs

- [Repository overview](../architecture/overview)
- [Pipeline goldens (testing)](../testing/pipeline-goldens) — `case.json`, harness, freeze tool
- [tests/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/tests/README.md)
- [testdata/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/testdata/README.md)
