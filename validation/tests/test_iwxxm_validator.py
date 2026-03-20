"""Unit tests for iwxxmValidator (filesystem layout + mocked Java)."""

import os
from unittest import mock

import iwxxmValidator as iv
import pytest


def _minimal_validation_tree(base: "os.PathLike[str]") -> None:
    base = str(base)
    os.makedirs(os.path.join(base, "bin"), exist_ok=True)
    open(os.path.join(base, "bin", "crux-1.3-all.jar"), "wb").close()
    os.makedirs(os.path.join(base, "externalSchemas"), exist_ok=True)
    os.makedirs(os.path.join(base, "schemas", "2023-1"), exist_ok=True)
    open(os.path.join(base, "schemas", "2023-1", "iwxxm.xsd"), "w").write("<schema/>")
    os.makedirs(os.path.join(base, "schematrons", "2023-1"), exist_ok=True)
    open(os.path.join(base, "schematrons", "2023-1", "iwxxm.sch"), "w").write("<sch/>")
    open(os.path.join(base, "catalog.template.xml"), "w").write(
        "${INSTALL_DIR}\n${IWXXM_VERSION}\n${IWXXM_VERSION_DIR}"
    )


def test_main_exits_when_missing_crux(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _minimal_validation_tree(tmp_path)
    os.remove(os.path.join(tmp_path, "bin", "crux-1.3-all.jar"))

    class Args:
        fetch = False
        version = "2023-1"
        directory = str(tmp_path / "xml")
        noGMLChecks = True
        useInternet = False
        keep = False

    (tmp_path / "xml").mkdir()
    with pytest.raises(SystemExit) as ei:
        iv.main(Args())
    assert ei.value.code == 1


def test_validate_xml_files_runs_java_and_skips_gml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _minimal_validation_tree(tmp_path)
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<root/>", encoding="utf-8")

    class Args:
        directory = str(xml_dir)
        version = "2023-1"
        keep = True
        noGMLChecks = True
        useInternet = False

    calls = []

    def fake_system(cmd):
        calls.append(cmd)
        return 0

    monkeypatch.setattr(iv.os, "system", fake_system)
    rc = iv.validate_xml_files(Args())
    assert rc == 0
    assert calls, "expected java/crux invocation"
    assert "crux-1.3-all.jar" in calls[0]
    assert "iwxxm.sch" in calls[0]


def test_validate_xml_files_gml_branch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _minimal_validation_tree(tmp_path)
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<root/>", encoding="utf-8")

    class Args:
        directory = str(xml_dir)
        version = "2023-1"
        keep = True
        noGMLChecks = False
        useInternet = False

    monkeypatch.setattr(iv.os, "system", lambda cmd: 0)
    with mock.patch.object(iv.checkGMLReferences, "check_GML_references", return_value=0):
        rc = iv.validate_xml_files(Args())
    assert rc == 0


def test_validate_xml_files_failed_java(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _minimal_validation_tree(tmp_path)
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<root/>", encoding="utf-8")

    class Args:
        directory = str(xml_dir)
        version = "2023-1"
        keep = True
        noGMLChecks = True
        useInternet = False

    monkeypatch.setattr(iv.os, "system", lambda cmd: 256)
    rc = iv.validate_xml_files(Args())
    assert rc == 1
