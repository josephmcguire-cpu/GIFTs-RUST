# Root `tests/` — integration, E2E, performance

Unit tests live next to each area:

- `gifts/tests/` — encoders, bulletin, common utilities
- `validation/tests/` — `iwxxmValidator.py`, GML helpers, Schematron path checks
- `demo/tests/` — `demo1.py` / `iwxxmd.py` (watchdog paths mocked)

This directory holds **cross-cutting** suites:

| Path | Markers | Purpose |
|------|---------|---------|
| `tests/e2e/` | `@pytest.mark.e2e` | TAC → `encode` → XML on disk → `validation/iwxxmValidator.py` (needs Java + local `schemas/` / `schematrons/` trees or skips) |
| `tests/perf/` | `@pytest.mark.perf` | `pytest-benchmark` timings (optional / scheduled CI) |

Run everything (excluding perf by default):

```bash
pip install -e ".[test]"
pytest gifts/tests validation/tests demo/tests tests/e2e -m "not perf"
```

Coverage gates (**≥99%** line coverage per tree) are configured in `Makefile` targets and `.github/workflows/test-*.yml`.
