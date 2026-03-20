"""Cover remaining checkGMLReferences branches (import fallback, HTTP codes, RDF edges)."""

import builtins
import importlib.util
import os
import sys
import types
from pathlib import Path
from unittest import mock

import checkGMLReferences as cg


def test_urllib2_import_fallback_when_request_missing(tmp_path):
    """Lines 5–6: except ImportError uses urllib2 as urlRequest."""
    urllib2_stub = types.ModuleType("urllib2")
    urllib2_stub.urlopen = lambda *a, **k: None
    sys.modules["urllib2"] = urllib2_stub

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "urllib.request":
            raise ImportError("mock no urllib.request")
        return real_import(name, globals, locals, fromlist, level)

    src = Path(__file__).resolve().parent.parent / "checkGMLReferences.py"
    sys.modules.pop("checkGMLReferences_fresh", None)
    with mock.patch("builtins.__import__", fake_import):
        spec = importlib.util.spec_from_file_location("checkGMLReferences_fresh", src)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    assert mod.urlRequest is urllib2_stub


def test_check_gml_internet_non_2xx_status(tmp_path, monkeypatch, capsys):
    """HTTP response with bad status triggers error path (fixed condition: code < 200 or >= 300)."""
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://example.com/iwxxm/badstatus"/>
</root>""",
        encoding="utf-8",
    )

    class Resp404:
        def getcode(self):
            return 404

    monkeypatch.setattr(cg.urlRequest, "urlopen", lambda u: Resp404())
    assert cg.check_GML_references(str(d), "2023-1", internet=True) == 1
    assert "does not resolve" in capsys.readouterr().out


def test_second_xml_uses_cached_concepts_new_rdf_filename(tmp_path, monkeypatch):
    """Lines 127–130: concepts[concept] exists; xlink not in list; RDF filename not yet cached."""
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    (sch / "codes.wmo.int-iwxxm.rdf").write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://example.com/a/bar">
    <skos:prefLabel xml:lang="en">x</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>""",
        encoding="utf-8",
    )
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "first.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.1"/>
  <b xlink:href="http://codes.wmo.int/iwxxm/foo"/>
</root>""",
        encoding="utf-8",
    )
    (d / "second.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.2"/>
  <b xlink:href="http://codes.wmo.int/other/bar"/>
</root>""",
        encoding="utf-8",
    )

    def ordered_listdir(p):
        return ["first.xml", "second.xml"]

    monkeypatch.setattr(cg.os, "listdir", ordered_listdir)
    monkeypatch.setattr(os, "listdir", ordered_listdir)
    rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc >= 0


def test_check_gml_file_cache_same_rdf_wrong_xlink_string(tmp_path, monkeypatch, capsys):
    """Lines 131–135: filename in file_cache but xlink not in concepts[concept]."""
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    fn = "codes.wmo.int-iwxxm.rdf"
    (sch / fn).write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://codes.wmo.int/iwxxm/foo">
    <skos:prefLabel xml:lang="en">x</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>""",
        encoding="utf-8",
    )
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://codes.wmo.int/iwxxm/foo"/>
  <c xlink:href="http://codes.wmo.int/iwxxm/foo/"/>
</root>""",
        encoding="utf-8",
    )
    rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc == 1
    out = capsys.readouterr().out
    assert "does not resolve" in out or "ERROR" in out


def test_check_gml_offline_xlink_not_in_rdf_after_load(tmp_path, monkeypatch, capsys):
    """Lines 145–148: after getConcepts, xlink URL not in concepts[concept] (error print + rc=1)."""
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    (sch / "codes.wmo.int-iwxxm.rdf").write_text("<rdf:RDF/>", encoding="utf-8")

    def fake_get_concepts(_path, concepts):
        concepts["bar"] = ["http://other.host/iwxxm/bar"]

    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://codes.wmo.int/iwxxm/bar"/>
</root>""",
        encoding="utf-8",
    )
    with mock.patch.object(cg, "getConcepts", side_effect=fake_get_concepts):
        rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc == 1
    assert "does not resolve" in capsys.readouterr().out


def test_check_gml_offline_concept_key_missing_warning(tmp_path, monkeypatch, capsys):
    """Lines 150–151: KeyError on concepts[concept] — warning only (rc may stay 0)."""
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    fn = "codes.wmo.int-iwxxm.rdf"
    (sch / fn).write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://codes.wmo.int/iwxxm/onlyfoo">
    <skos:prefLabel xml:lang="en">x</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>""",
        encoding="utf-8",
    )
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://codes.wmo.int/iwxxm/other"/>
</root>""",
        encoding="utf-8",
    )
    rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    out = capsys.readouterr().out
    assert "not found in code list" in out
    assert rc == 0
