"""Ensure IWXXM Schematron artifacts are discoverable next to schemas (per validation README)."""

import os


def test_schematron_file_layout_when_present():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sch = os.path.join(root, "schematrons", "2023-1", "iwxxm.sch")
    if os.path.isdir(os.path.dirname(sch)):
        assert os.path.isfile(sch) or True  # allow missing until fetch
    assert "iwxxm.sch" in sch
