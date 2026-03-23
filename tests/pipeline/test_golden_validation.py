"""Optional IWXXM validation (CRUX) for committed golden XML — same bar as validation/README.md."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tests.pipeline.golden_harness import load_case_json, pipeline_case_paths, repo_root


def _validation_root() -> Path:
    return repo_root() / "validation"


def _schemas_ready(version: str) -> bool:
    root = _validation_root()
    return (root / "schemas" / version / "iwxxm.xsd").is_file() and (
        root / "schematrons" / version / "iwxxm.sch"
    ).is_file()


def _crux_jar() -> Path:
    return _validation_root() / "bin" / "crux-1.3-all.jar"


@pytest.mark.parametrize("case_path", pipeline_case_paths(), ids=lambda p: p.parent.name)
@pytest.mark.integration
def test_golden_directory_validates_with_iwxxm_validator(case_path: Path):
    data = load_case_json(case_path)
    version = data["iwxxm_validator_version"]
    gdir = case_path.parent / "golden"

    if not _crux_jar().is_file():
        pytest.skip("CRUX jar not present under validation/bin/")
    if not _schemas_ready(version):
        pytest.skip(f"IWXXM schemas/schematron not present for version {version}")

    root = _validation_root()
    proc = subprocess.run(
        [sys.executable, "iwxxmValidator.py", "--noGMLChecks", "-v", version, str(gdir)],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
