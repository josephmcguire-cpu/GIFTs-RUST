# `testdata/` — portable pipeline regression contract

This directory holds **frozen checkpoints** for the TAC → decode → IWXXM path so another implementation (e.g. Rust) can regression-test against the same inputs and expected outputs **without using Python** in the test runner.

## Layout

- **`pipeline/<case_id>/case.json`** — Schema version `schema: 1`. Contains:
  - `input` — full message (WMO AHL + TAC)
  - `geo_db` — ICAO → pipe-separated aerodrome metadata (METAR/TAF); `{}` for advisories
  - `freeze_time` — nominal UTC instant used with the deterministic harness (see below)
  - `ahl` — bulletin/AHL fields after merge with product `T1T2`
  - `reports[]` — per matched TAC: `tac`, `decoded` (enriched dict), `iwxxm_xml`
  - `iwxxm_validator_version` — must match `gifts.common.xmlConfig.IWXXM_VALIDATOR_VERSION` and `validation/schemas/<version>/`
  - `xml_config_overrides` — encoder-affecting flags used when the golden was built; the harness always applies a baseline (`TRANSLATOR: false`, `TITLES: 0` matching [xmlConfig.py](../gifts/common/xmlConfig.py) defaults) so pytest order cannot leak state from other tests. Override per case if you need translator or `xlink:title` behaviour.
  - `validation_profile` — how to run CRUX validation (see [validation/README.md](../validation/README.md))

- **`pipeline/<case_id>/golden/<n>.xml`** — Same IWXXM document(s) as `reports[n].iwxxm_xml` for tools that prefer plain XML on disk.

- **`pipeline/<case_id>/input.txt`** — Copy of `input` for editors.

## Consumers (non-Python)

1. Read `case.json` (UTF-8).
2. For each report, compare your port’s `decoded` structure and IWXXM XML to `decoded` / `iwxxm_xml` (or diff `golden/*.xml`).
3. Optionally validate XML with **Java CRUX** the same way as `validation/iwxxmValidator.py` (schema + Schematron, e.g. `--noGMLChecks` in CI). Use `-v <iwxxm_validator_version>` from the JSON. Reproduce the Java command line from [validation/iwxxmValidator.py](../validation/iwxxmValidator.py) if you are not invoking Python.

## Regenerators (Python)

After changing encoders or adding cases in [`tests/pipeline/golden_cases.py`](../tests/pipeline/golden_cases.py):

```bash
pip install -e ".[test]"
python tools/freeze_pipeline_cases.py
```

Optional: validate written XML when `validation/bin/crux-1.3-all.jar` and schemas exist:

```bash
python tools/freeze_pipeline_cases.py --validate
```

The harness uses **freezegun**, a **deterministic `getUUID` patch**, and a **`time.strftime` patch** for the decoder `translationTime` pattern so outputs are stable across machines.

## CI in this repo

[`tests/pipeline/`](../tests/pipeline/) replays every `case.json` under the same harness and checks decoded + XML equality. [`tests/pipeline/test_golden_validation.py`](../tests/pipeline/test_golden_validation.py) runs `iwxxmValidator.py` on each `golden/` directory when CRUX and schemas are present (otherwise skipped).
