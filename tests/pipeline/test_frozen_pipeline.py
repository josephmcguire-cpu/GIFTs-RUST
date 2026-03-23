"""Replay testdata/pipeline cases under the same deterministic harness as regeneration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.pipeline.golden_harness import (
    assert_reports_match,
    build_case_document,
    collect_reports,
    load_case_json,
    make_encoder,
    pipeline_case_paths,
    replay_determinism_for_case,
    repo_root,
)


def _cases():
    return list(pipeline_case_paths())


@pytest.mark.parametrize("case_path", _cases(), ids=lambda p: p.parent.name)
def test_frozen_case_matches_disk(case_path: Path):
    data = load_case_json(case_path)
    product = data["product"]
    text = data["input"]
    geo_db = data.get("geo_db") or {}
    receipt_time = data.get("receipt_time")

    with replay_determinism_for_case(data):
        enc = make_encoder(product, geo_db)
        actual = collect_reports(enc, text, receipt_time=receipt_time)

    expected_reports = data["reports"]
    assert_reports_match(expected_reports, actual)


def test_golden_case_definitions_match_committed_files():
    """Regeneration must not drift from golden_cases.py without running the freeze script."""
    from tests.pipeline.golden_cases import GOLDEN_CASE_INPUTS

    for spec in GOLDEN_CASE_INPUTS:
        path = repo_root() / "testdata" / "pipeline" / spec["case_id"] / "case.json"
        assert path.is_file(), f"Missing {path} — run python tools/freeze_pipeline_cases.py"
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        fresh = build_case_document(spec)
        assert json.dumps(on_disk, sort_keys=True) == json.dumps(fresh, sort_keys=True), (
            "Committed case.json for {} differs from golden_cases.py — regenerate".format(spec["case_id"])
        )


@pytest.mark.parametrize("case_path", _cases(), ids=lambda p: p.parent.name)
def test_golden_xml_files_match_embedded(case_path: Path):
    data = load_case_json(case_path)
    golden_dir = case_path.parent / "golden"
    for i, rep in enumerate(data["reports"]):
        p = golden_dir / f"{i}.xml"
        assert p.is_file()
        assert p.read_text(encoding="utf-8") == (rep.get("iwxxm_xml") or "")
