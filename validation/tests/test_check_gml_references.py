"""Tests for checkGMLReferences."""

import checkGMLReferences as cg


def test_no_xml_files_returns_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "empty"
    d.mkdir()
    rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc == 1


def test_readIgnoredURLs_skips_comments(tmp_path):
    p = tmp_path / "ign.txt"
    p.write_text("# c\n\nhttp://example.com\n", encoding="utf-8")
    urls = cg.readIgnoredURLs(str(p))
    assert urls == ["http://example.com"]


def test_minimal_xml_uuid_hrefs(tmp_path, monkeypatch):
    """Two elements: gml:id and matching xlink href — happy path."""
    monkeypatch.chdir(tmp_path)
    xml = tmp_path / "a.xml"
    xml.write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <feature gml:id="uuid.111"/>
  <ref xlink:href="#uuid.111"/>
</root>""",
        encoding="utf-8",
    )
    rc = cg.check_GML_references(str(tmp_path), "2023-1", internet=False)
    assert rc == 0
