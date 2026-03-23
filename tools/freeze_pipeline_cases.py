#!/usr/bin/env python3
"""Regenerate testdata/pipeline/*/case.json and golden/*.xml from tests/pipeline/golden_cases.py.

Run from repository root:
  python tools/freeze_pipeline_cases.py

Requires: pip install -e ".[test]" (freezegun).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = _repo_root()
    sys.path.insert(0, str(root))

    parser = argparse.ArgumentParser(description="Regenerate pipeline golden testdata.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="After writing files, run iwxxmValidator.py on golden XML if CRUX and schemas exist.",
    )
    args = parser.parse_args()

    from tests.pipeline.golden_cases import GOLDEN_CASE_INPUTS
    from tests.pipeline.golden_harness import build_case_document, repo_root

    assert repo_root() == root

    out_root = root / "testdata" / "pipeline"
    out_root.mkdir(parents=True, exist_ok=True)

    for spec in GOLDEN_CASE_INPUTS:
        payload = build_case_document(spec)
        case_dir = out_root / spec["case_id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        golden_dir = case_dir / "golden"
        golden_dir.mkdir(exist_ok=True)

        for i, rep in enumerate(payload["reports"]):
            xml = rep.get("iwxxm_xml") or ""
            (golden_dir / f"{i}.xml").write_text(xml, encoding="utf-8")

        (case_dir / "case.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (case_dir / "input.txt").write_text(spec["input"], encoding="utf-8")

        print("Wrote", case_dir)

    if args.validate:
        import gifts.common.xmlConfig as des

        val = root / "validation"
        jar = val / "bin" / "crux-1.3-all.jar"
        ver = des.IWXXM_VALIDATOR_VERSION
        xsd = val / "schemas" / ver / "iwxxm.xsd"
        if jar.is_file() and xsd.is_file():
            for spec in GOLDEN_CASE_INPUTS:
                gdir = out_root / spec["case_id"] / "golden"
                proc = subprocess.run(
                    [sys.executable, "iwxxmValidator.py", "--noGMLChecks", "-v", ver, str(gdir)],
                    cwd=val,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if proc.returncode != 0:
                    print(proc.stdout + proc.stderr, file=sys.stderr)
                    return proc.returncode
            print("iwxxmValidator passed for all golden directories.")
        else:
            print(f"Skipping --validate (missing jar or schemas/{ver})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
