"""Extra branches in xmlUtilities for coverage."""

import time

from gifts.common import xmlUtilities as xu


def test_fix_date_january_rolls_year(monkeypatch):
    tms = [2021, 1, 15, 12, 0, 0, 0, 0, -1]
    monkeypatch.setattr(xu.time, "time", lambda: time.mktime((2021, 2, 20, 0, 0, 0, 0, 0, -1)))
    xu.fix_date(tms)
    assert tms[1] == 2


def test_fix_date_december_next_month(monkeypatch):
    tms = [2021, 12, 15, 12, 0, 0, 0, 0, -1]
    monkeypatch.setattr(xu.time, "time", lambda: time.mktime((2022, 1, 20, 0, 0, 0, 0, 0, -1)))
    xu.fix_date(tms)
    assert tms[1] == 1 and tms[0] == 2022


def test_computeLatLon_nlon_gt_180():
    s = xu.computeLatLon(0.0, 179.0, 90, 5000.0, radius=3440.0)
    assert isinstance(s, str)


def test_checkVisibility_else_10000_branch():
    assert xu.checkVisibility(10000) == 10000


def test_parseCodeRegistry_preferred_non_en_label(tmp_path):
    rdf = tmp_path / "codes.wmo.int-test.rdf"
    rdf.write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:xml="http://www.w3.org/XML/1998/namespace">
  <skos:Concept rdf:about="http://example.com/vocab/x">
    <rdfs:label xml:lang="fr">Bonjour</rdfs:label>
    <rdfs:label xml:lang="en">Hello</rdfs:label>
  </skos:Concept>
</rdf:RDF>""",
        encoding="utf-8",
    )
    codes = xu.parseCodeRegistryTables(str(tmp_path), ["test"], preferredLanguage="fr")
    assert "test" in codes


def test_parseCodeRegistry_fallback_nolang(tmp_path):
    rdf = tmp_path / "codes.wmo.int-test2.rdf"
    rdf.write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:xml="http://www.w3.org/XML/1998/namespace">
  <skos:Concept rdf:about="http://example.com/vocab/y">
    <rdfs:label>Only</rdfs:label>
  </skos:Concept>
</rdf:RDF>""",
        encoding="utf-8",
    )
    codes = xu.parseCodeRegistryTables(str(tmp_path), ["test2"], preferredLanguage="en")
    assert "test2" in codes
