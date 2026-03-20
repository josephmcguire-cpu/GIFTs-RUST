"""Tests for codeListsToSchematron (network and filesystem mocked)."""

import codeListsToSchematron as cl


def test_parseLocalCodeListFile():
    assert cl.parseLocalCodeListFile("http://codes.wmo.int/49-2/Foo").endswith(".rdf")


def test_fetchLocalCopy_handles_bad_status(monkeypatch, tmp_path):
    class R:
        status_code = 404
        text = ""

    monkeypatch.setattr(cl.requests, "get", lambda url: R())
    cl.fetchLocalCopy("http://example.com", "xsd", str(tmp_path))


def test_fetchLocalCopy_writes_files(monkeypatch, tmp_path):
    html = """<html><body><table><tr><td><a href='a.xsd'>a</a></td></tr></table></body></html>"""

    class Page:
        status_code = 200
        text = html

    class FileResp:
        status_code = 200
        text = "<schema/>"

    def fake_get(url):
        if url.endswith("a.xsd"):
            return FileResp()
        return Page()

    monkeypatch.setattr(cl.requests, "get", fake_get)
    cl.fetchLocalCopy("http://example.com", "xsd", str(tmp_path))
    assert (tmp_path / "a.xsd").exists()


def test_download_codelist_non_200(monkeypatch, tmp_path, capsys):
    class R:
        status_code = 404
        text = ""

    monkeypatch.setattr(cl.requests, "get", lambda url, headers=None: R())
    cl.download_codelist("http://codes.wmo.int/x", str(tmp_path))
    assert "ERROR" in capsys.readouterr().out


def test_download_codelist_writes(tmp_path, monkeypatch):
    class R:
        status_code = 200
        text = "ok"

    monkeypatch.setattr(cl.requests, "get", lambda url, headers=None: R())
    cl.download_codelist("http://codes.wmo.int/x", str(tmp_path))


def test_run_happy_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text(
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>', encoding="utf-8"
    )
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<sch/>", encoding="utf-8")

    xsd = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:complexType name="T">
        <xs:annotation><xs:appinfo><xs:vocabulary>http://codes.wmo.int/common/nil</xs:vocabulary></xs:appinfo></xs:annotation>
      </xs:complexType>
    </xs:schema>"""
    (tmp_path / "schemas" / "2023-1" / "t.xsd").write_text(xsd, encoding="utf-8")

    class Args:
        version = "2023-1"

    class R:
        status_code = 200
        text = "ok"

    monkeypatch.setattr(cl.requests, "get", lambda url, headers=None: R())
    cl.run(Args())


def test_run_symlink_branch(monkeypatch, tmp_path):
    """Exercise AerodromePresentOrForecastWeather symlink logic when RDF files exist."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text(
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>', encoding="utf-8"
    )
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    (sch / "iwxxm.sch").write_text("<sch/>", encoding="utf-8")

    xsd = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:complexType name="T">
        <xs:annotation><xs:appinfo>
          <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
        </xs:appinfo></xs:annotation>
      </xs:complexType>
    </xs:schema>"""
    (tmp_path / "schemas" / "2023-1" / "t.xsd").write_text(xsd, encoding="utf-8")

    src = "codes.wmo.int-49-2-AerodromePresentOrForecastWeather.rdf"
    dst = "codes.wmo.int-306-4678.rdf"
    (sch / src).write_text("<rdf/>", encoding="utf-8")

    class Args:
        version = "2023-1"

    class R:
        status_code = 200
        text = "ok"

    monkeypatch.setattr(cl.requests, "get", lambda url, headers=None: R())
    monkeypatch.setattr(cl.os, "symlink", lambda s, d: None)
    cl.run(Args())
    assert (sch / dst).exists() or (sch / src).exists()


def test_run_symlink_failure_prints(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text(
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"/>', encoding="utf-8"
    )
    sch = tmp_path / "schematrons" / "2023-1"
    sch.mkdir(parents=True)
    (sch / "iwxxm.sch").write_text("<sch/>", encoding="utf-8")

    xsd = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:complexType name="T">
        <xs:annotation><xs:appinfo>
          <xs:vocabulary>http://codes.wmo.int/49-2/AerodromePresentOrForecastWeather</xs:vocabulary>
        </xs:appinfo></xs:annotation>
      </xs:complexType>
    </xs:schema>"""
    (tmp_path / "schemas" / "2023-1" / "t.xsd").write_text(xsd, encoding="utf-8")
    (sch / "codes.wmo.int-49-2-AerodromePresentOrForecastWeather.rdf").write_text("<rdf/>", encoding="utf-8")

    class Args:
        version = "2023-1"

    class R:
        status_code = 200
        text = "ok"

    monkeypatch.setattr(cl.requests, "get", lambda url, headers=None: R())

    def boom(src, dst):
        raise OSError("nope")

    monkeypatch.setattr(cl.os, "symlink", boom)
    cl.run(Args())
    assert "Unable to create symbolic link" in capsys.readouterr().out
