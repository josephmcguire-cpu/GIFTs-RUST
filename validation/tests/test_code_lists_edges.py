"""Remaining branches in codeListsToSchematron."""

import sys
from unittest import mock

import codeListsToSchematron as cl
import pytest


def test_run_exits_on_bad_dirs(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cl.os.path, "isdir", lambda p: False)

    class Args:
        version = "2023-1"

    with pytest.raises(SystemExit):
        cl.run(Args())


def test_fetchLocalCopy_unicode_encode_in_write(monkeypatch, tmp_path):
    html = """<html><body><table><tr><td><a href='a.xsd'>a</a></td></tr></table></body></html>"""

    class Page:
        status_code = 200
        text = html

    calls = {"n": 0}

    def fake_get(url):
        calls["n"] += 1
        if calls["n"] == 1:
            return Page()
        return type("F", (), {"status_code": 200, "text": "café"})()

    monkeypatch.setattr(cl.requests, "get", fake_get)

    class Boom:
        def write(self, s):
            if isinstance(s, str):
                raise UnicodeEncodeError("ascii", "", 0, 1, "x")
            return len(s)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    with mock.patch("builtins.open", return_value=Boom()):
        cl.fetchLocalCopy("http://example.com", "xsd", str(tmp_path))


def test_download_codelist_unicode_encode(monkeypatch, tmp_path):
    class R:
        status_code = 200
        text = "café"

    monkeypatch.setattr(cl.requests, "get", lambda url, headers=None: R())

    class Boom:
        def write(self, s):
            if isinstance(s, str):
                raise UnicodeEncodeError("ascii", "", 0, 1, "x")
            return len(s)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    with mock.patch("builtins.open", return_value=Boom()):
        cl.download_codelist("http://codes.wmo.int/x", str(tmp_path))


def test_symlink_ms_win(monkeypatch):
    class FakeCtypes:
        WinError = OSError
        c_wchar_p = object()
        c_uint32 = object()
        c_ubyte = object()

        class windll:
            class kernel32:
                CreateSymbolicLinkW = staticmethod(lambda *a, **k: 0)

    monkeypatch.setitem(sys.modules, "ctypes", FakeCtypes)
    with pytest.raises(OSError):
        cl.symlink_ms("/a", "/b")


def test_symlink_ms_success(monkeypatch):
    """Lines 169–172: CreateSymbolicLinkW returns non-zero (success)."""

    class FakeCtypes:
        c_wchar_p = object()
        c_uint32 = object()
        c_ubyte = object()

        class windll:
            class kernel32:
                CreateSymbolicLinkW = staticmethod(lambda *a, **k: 1)

    monkeypatch.setitem(sys.modules, "ctypes", FakeCtypes)
    cl.symlink_ms("/tmp/src", "/tmp/dst")


def test_fetchLocalCopy_individual_file_non_200(monkeypatch, tmp_path, capsys):
    """Line 137: schema file download returns non-200."""
    html = """<html><body><table><tr><td><a href='a.xsd'>a</a></td></tr></table></body></html>"""

    class Page:
        status_code = 200
        text = html

    def fake_get(url):
        if url.endswith("a.xsd"):
            return type("Bad", (), {"status_code": 404, "text": ""})()
        return Page()

    monkeypatch.setattr(cl.requests, "get", fake_get)
    cl.fetchLocalCopy("http://example.com", "xsd", str(tmp_path))
    assert "Unable to write" in capsys.readouterr().out


def test_run_py2_nt_sets_symlink_ms(monkeypatch, tmp_path):
    """Line 21: Python 2 on Windows aliases os.symlink to symlink_ms."""
    monkeypatch.chdir(tmp_path)

    class VI:
        major = 2

    monkeypatch.setattr(cl.sys, "version_info", VI())
    monkeypatch.setattr(cl.os, "name", "nt")
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
    assert cl.os.symlink is cl.symlink_ms


def test_run_downloads_schema_and_schematron_when_missing(monkeypatch, tmp_path):
    """Lines 59–67: fetchSchemaFiles and fetchSchematronFile call fetchLocalCopy."""
    monkeypatch.chdir(tmp_path)
    html_xsd = """<html><body><table><tr><td><a href='iwxxm.xsd'>x</a></td></tr></table></body></html>"""
    html_sch = """<html><body><table><tr><td><a href='iwxxm.sch'>s</a></td></tr></table></body></html>"""
    schema_xsd = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:complexType name="T">
        <xs:annotation><xs:appinfo><xs:vocabulary>http://codes.wmo.int/common/nil</xs:vocabulary></xs:appinfo></xs:annotation>
      </xs:complexType>
    </xs:schema>"""

    def fake_get(url, headers=None):
        u = str(url)
        if "iwxxm/2023-1/rule" in u or u.endswith("/rule"):
            return type("P", (), {"status_code": 200, "text": html_sch})()
        if u.endswith("/2023-1") or ("iwxxm/2023-1" in u and "rule" not in u):
            return type("P", (), {"status_code": 200, "text": html_xsd})()
        if u.endswith("iwxxm.xsd"):
            return type("P", (), {"status_code": 200, "text": schema_xsd})()
        if u.endswith("iwxxm.sch"):
            return type("P", (), {"status_code": 200, "text": "<sch/>"})()
        if "codes.wmo.int" in u:
            return type("P", (), {"status_code": 200, "text": "<rdf/>"})()
        return type("P", (), {"status_code": 404, "text": ""})()

    monkeypatch.setattr(cl.requests, "get", fake_get)

    class Args:
        version = "2023-1"

    cl.run(Args())
    assert (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").exists()
    assert (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").exists()
