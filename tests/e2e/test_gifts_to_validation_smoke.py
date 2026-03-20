"""E2E: gifts encode -> XML on disk -> iwxxmValidator (optional if Java + CRUX present)."""

import os
import subprocess
import sys

import pytest

from gifts.METAR import Encoder as ME

pytestmark = pytest.mark.e2e


@pytest.fixture
def geo_db():
    return {"BIAR": "AKUREYRI|AEY|AKI|65.67 -18.07 27"}


def test_metar_encodes_to_bulletin(geo_db):
    text = """SAXX99 XXXX 151200
METAR BIAR 290000Z 33003KT 280V010 9999 OVC032 04/M00 Q1023=
"""
    enc = ME(geo_db)
    b = enc.encode(text)
    assert len(b) >= 1


def _validation_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "validation"))


def _schemas_ready(version: str = "2023-1") -> bool:
    root = _validation_root()
    return os.path.isfile(os.path.join(root, "schemas", version, "iwxxm.xsd")) and os.path.isfile(
        os.path.join(root, "schematrons", version, "iwxxm.sch")
    )


@pytest.mark.skipif(
    not os.path.isfile(os.path.join(_validation_root(), "bin", "crux-1.3-all.jar")),
    reason="CRUX jar not present",
)
def test_iwxxm_validator_invocation_help():
    root = _validation_root()
    proc = subprocess.run(
        [sys.executable, "iwxxmValidator.py", "-h"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "Rudimentary" in proc.stdout or "validation" in proc.stdout.lower()


@pytest.mark.skipif(
    not os.path.isfile(os.path.join(_validation_root(), "bin", "crux-1.3-all.jar")),
    reason="CRUX jar not present",
)
@pytest.mark.skipif(
    not _schemas_ready(),
    reason="IWXXM schemas/schematron not present under validation/ (run iwxxmValidator.py -f once)",
)
def test_metar_encode_write_then_validate(tmp_path, geo_db):
    """Full pipeline: METAR bulletin written as pure XML, validated with CRUX (no GML internet checks)."""
    text = """SAXX99 XXXX 151200
METAR BIAR 290000Z 33003KT 280V010 9999 OVC032 04/M00 Q1023=
"""
    enc = ME(geo_db)
    bulletin = enc.encode(text)
    out_dir = tmp_path / "xmlout"
    out_dir.mkdir()
    bulletin.write(str(out_dir), header=False)

    root = _validation_root()
    proc = subprocess.run(
        [sys.executable, "iwxxmValidator.py", "--noGMLChecks", str(out_dir)],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
