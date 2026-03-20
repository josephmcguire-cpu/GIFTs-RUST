"""Deep coverage for checkGMLReferences."""

import xml.etree.ElementTree as ET
from unittest import mock

import checkGMLReferences as cg


def test_getConcepts_populates(monkeypatch):
    """ET.iterfind path in getConcepts matches production; use a stub tree that yields a Concept."""
    concept = ET.Element("{http://www.w3.org/2004/02/skos/core#}Concept")
    concept.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "http://codes.wmo.int/x/foo")

    class FakeTree:
        def iterfind(self, path):
            return [concept]

    monkeypatch.setattr(cg.ET, "parse", lambda _path: FakeTree())
    concepts = {}
    cg.getConcepts("ignored.rdf", concepts)
    assert "foo" in concepts


def test_readIgnoredURLs_empty_file(tmp_path):
    p = tmp_path / "i.txt"
    p.write_text("", encoding="utf-8")
    assert cg.readIgnoredURLs(str(p)) == []


def test_check_gml_success_uuid_links(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="#uuid.111"/>
</root>""",
        encoding="utf-8",
    )
    assert cg.check_GML_references(str(d), "2023-1", internet=False) == 0


def test_check_gml_bad_uuid_ref(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.222"/>
  <b xlink:href="#uuid.111"/>
</root>""",
        encoding="utf-8",
    )
    assert cg.check_GML_references(str(d), "2023-1", internet=False) == 1
    assert "Missing gml ID" in capsys.readouterr().out


def test_check_gml_ignored_external_url(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ignoredURLs.txt").write_text("http://codes.wmo.int\n", encoding="utf-8")
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://codes.wmo.int/49-2/foo"/>
</root>""",
        encoding="utf-8",
    )
    assert cg.check_GML_references(str(d), "2023-1", internet=False) == 0


def test_check_gml_internet_bad_url(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://example.invalid.test/iwxxm/nope"/>
</root>""",
        encoding="utf-8",
    )

    class Boom:
        def getcode(self):
            return 404

    def fake_urlopen(url):
        raise OSError("nxdomain")

    monkeypatch.setattr(cg.urlRequest, "urlopen", fake_urlopen)
    assert cg.check_GML_references(str(d), "2023-1", internet=True) == 1
    assert "does not resolve" in capsys.readouterr().out


def test_check_gml_internet_good_code(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://example.com/iwxxm/ok"/>
</root>""",
        encoding="utf-8",
    )

    class Resp:
        def getcode(self):
            return 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(cg.urlRequest, "urlopen", lambda u: Resp())
    assert cg.check_GML_references(str(d), "2023-1", internet=True) == 0


def test_check_gml_offline_rdf_resolves(tmp_path, monkeypatch):
    """Offline mode: xlink to codes.wmo.int with RDF listing the concept."""
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    fn = "codes.wmo.int-iwxxm.rdf"
    rdf_path = sch / fn
    rdf_path.write_text(
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
</root>""",
        encoding="utf-8",
    )
    assert cg.check_GML_references(str(d), "2023-1", internet=False) == 0


def test_check_gml_offline_missing_rdf_ioerror(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    d = tmp_path / "xmld"
    d.mkdir()
    (d / "a.xml").write_text(
        """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://codes.wmo.int/missing/only/path"/>
</root>""",
        encoding="utf-8",
    )
    with mock.patch("checkGMLReferences.getConcepts", side_effect=OSError("no file")):
        rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc == 1
    out = capsys.readouterr().out
    assert "Possible invalid reference" in out or "WARNED" in out


def test_check_gml_offline_concept_not_in_rdf(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    fn = "codes.wmo.int-iwxxm-bar.rdf"
    (sch / fn).write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://codes.wmo.int/iwxxm/other">
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
  <b xlink:href="http://codes.wmo.int/iwxxm/wanted"/>
</root>""",
        encoding="utf-8",
    )
    rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc == 1


def test_check_gml_file_cache_branch(tmp_path, monkeypatch):
    """Second xlink same concept uses file_cache path."""
    monkeypatch.chdir(tmp_path)
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    fn = "codes.wmo.int-iwxxm-baz.rdf"
    (sch / fn).write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://codes.wmo.int/iwxxm/baz">
    <skos:prefLabel xml:lang="en">x</skos:prefLabel>
  </skos:Concept>
</rdf:RDF>""",
        encoding="utf-8",
    )
    d = tmp_path / "xmld"
    d.mkdir()
    xml = """<?xml version="1.0"?>
<root xmlns:gml="http://www.opengis.net/gml/3.2"
      xmlns:xlink="http://www.w3.org/1999/xlink">
  <a gml:id="uuid.111"/>
  <b xlink:href="http://codes.wmo.int/iwxxm/baz"/>
  <c xlink:href="http://codes.wmo.int/iwxxm/missing"/>
</root>"""
    (d / "a.xml").write_text(xml, encoding="utf-8")
    rc = cg.check_GML_references(str(d), "2023-1", internet=False)
    assert rc >= 1
