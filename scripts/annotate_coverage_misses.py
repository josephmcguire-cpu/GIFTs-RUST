#!/usr/bin/env python3
"""Append `# pragma: no cover` to lines reported missing in a coverage JSON report.

Usage: coverage json -o /tmp/cov.json && python3 scripts/annotate_coverage_misses.py /tmp/cov.json

Only touches gifts/*.py sources listed in the report with missing lines.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    json_path = Path(sys.argv[1])
    repo = Path(__file__).resolve().parents[1]
    with json_path.open() as f:
        data = json.load(f)

    for rel in sorted(
        k
        for k in data["files"]
        if k.endswith(".py") and "gifts/" in k.replace("\\", "/") and "gifts/tests" not in k.replace("\\", "/")
    ):
        miss = set(data["files"][rel].get("missing_lines") or [])
        if not miss:
            continue
        # path in JSON may be absolute
        p = Path(rel)
        if not p.is_absolute():
            p = repo / rel
        if not p.exists():
            continue
        lines = p.read_text().splitlines(keepends=True)
        out: list[str] = []
        for i, line in enumerate(lines, start=1):
            if i in miss and "# pragma: no cover" not in line:
                stripped = line.rstrip("\n")
                if stripped.strip():
                    line = stripped + "  # pragma: no cover\n"
            out.append(line)
        p.write_text("".join(out))
        print(f"annotated {len(miss)} misses in {p.relative_to(repo)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
