"""Additional iwxxmValidator main() and validate_xml_files branches."""

import iwxxmValidator as iv
import pytest


def _args(**kw):
    defaults = dict(
        fetch=False,
        version="2023-1",
        directory="xmldir",
        noGMLChecks=True,
        useInternet=False,
        keep=False,
    )
    defaults.update(kw)
    return type("Args", (), defaults)()


def test_main_exits_without_layout(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as ei:
        iv.main(_args())
    assert ei.value.code == 1
    assert "bin" in capsys.readouterr().out


def test_main_fetch_calls_code_lists(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "out"
    xml_dir.mkdir()
    calls = []

    def fake_run(a):
        calls.append(a)

    monkeypatch.setattr(iv.codeLists, "run", fake_run)
    monkeypatch.setattr(iv, "validate_xml_files", lambda a: 0)

    with pytest.raises(SystemExit) as ei:
        iv.main(_args(fetch=True, directory=str(xml_dir)))
    assert ei.value.code == 0
    assert calls


def test_main_missing_schema_triggers_fetch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "out"
    xml_dir.mkdir()
    fetched = []

    def fake_run(a):
        fetched.append(True)
        (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text("<s/>", encoding="utf-8")
        (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<s/>", encoding="utf-8")

    monkeypatch.setattr(iv.codeLists, "run", fake_run)
    monkeypatch.setattr(iv, "validate_xml_files", lambda a: 0)

    with pytest.raises(SystemExit) as ei:
        iv.main(_args(fetch=False, directory=str(xml_dir)))
    assert ei.value.code == 0
    assert fetched


def test_main_failed_validation_message(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text("<s/>", encoding="utf-8")
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<s/>", encoding="utf-8")
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "out"
    xml_dir.mkdir()

    monkeypatch.setattr(iv, "validate_xml_files", lambda a: 2)
    with pytest.raises(SystemExit) as ei:
        iv.main(_args(directory=str(xml_dir)))
    assert ei.value.code == 2
    assert "FAILED" in capsys.readouterr().out


def test_validate_catalog_reuse_sets_keep(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text("<s/>", encoding="utf-8")
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<s/>", encoding="utf-8")
    cat = tmp_path / "catalog-2023-1.xml"
    cat.write_text("old", encoding="utf-8")
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<r/>", encoding="utf-8")

    a = _args(directory=str(xml_dir), keep=False)
    monkeypatch.setattr(iv.os, "system", lambda c: 0)
    monkeypatch.setattr(iv.checkGMLReferences, "check_GML_references", lambda *x, **y: 0)
    rc = iv.validate_xml_files(a)
    assert rc == 0
    assert a.keep is True


def test_validate_gml_check_failure_message(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text("<s/>", encoding="utf-8")
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<s/>", encoding="utf-8")
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<r/>", encoding="utf-8")

    a = _args(directory=str(xml_dir), noGMLChecks=False, keep=True)
    monkeypatch.setattr(iv.os, "system", lambda c: 0)
    monkeypatch.setattr(iv.checkGMLReferences, "check_GML_references", lambda *x, **y: 1)
    rc = iv.validate_xml_files(a)
    assert rc == 1
    assert "some files are not correct" in capsys.readouterr().out


def test_validate_removes_catalog_when_not_keep(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text("<s/>", encoding="utf-8")
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<s/>", encoding="utf-8")
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<r/>", encoding="utf-8")
    cat = tmp_path / "catalog-2023-1.xml"

    a = _args(directory=str(xml_dir), keep=False, noGMLChecks=True)
    monkeypatch.setattr(iv.os, "system", lambda c: 0)
    iv.validate_xml_files(a)
    assert not cat.exists()


def test_validate_gml_success_message(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "crux-1.3-all.jar").write_bytes(b"")
    (tmp_path / "externalSchemas").mkdir()
    (tmp_path / "schemas" / "2023-1").mkdir(parents=True)
    (tmp_path / "schemas" / "2023-1" / "iwxxm.xsd").write_text("<s/>", encoding="utf-8")
    (tmp_path / "schematrons" / "2023-1").mkdir(parents=True)
    (tmp_path / "schematrons" / "2023-1" / "iwxxm.sch").write_text("<s/>", encoding="utf-8")
    (tmp_path / "catalog.template.xml").write_text("${INSTALL_DIR}\n", encoding="utf-8")
    xml_dir = tmp_path / "xmldir"
    xml_dir.mkdir()
    (xml_dir / "a.xml").write_text("<r/>", encoding="utf-8")

    a = _args(directory=str(xml_dir), noGMLChecks=False, keep=True)
    monkeypatch.setattr(iv.os, "system", lambda c: 0)
    monkeypatch.setattr(iv.checkGMLReferences, "check_GML_references", lambda *x, **y: 0)
    iv.validate_xml_files(a)
    out = capsys.readouterr().out.lower()
    assert "successfuly" in out or "successfully" in out
