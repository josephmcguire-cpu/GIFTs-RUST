"""Keep testdata IWXXM validator version aligned with gifts.common.xmlConfig."""

from __future__ import annotations

import pytest

import gifts.common.xmlConfig as des
from tests.pipeline.golden_harness import load_case_json, pipeline_case_paths


@pytest.mark.parametrize("case_path", pipeline_case_paths(), ids=lambda p: p.parent.name)
def test_case_iwxxm_validator_version_matches_xmlconfig(case_path):
    data = load_case_json(case_path)
    assert data["iwxxm_validator_version"] == des.IWXXM_VALIDATOR_VERSION
