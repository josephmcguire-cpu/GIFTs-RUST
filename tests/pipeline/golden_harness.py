"""Deterministic capture/compare for TAC→IWXXM pipeline goldens (testdata/pipeline)."""

from __future__ import annotations

import json
import time as time_module
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import gifts.common.xmlConfig as des
import gifts.common.xmlUtilities as deu


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_for_json(obj):
    """Recursively produce JSON-compatible structures with string dict keys."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[str(k)] = normalize_for_json(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [normalize_for_json(x) for x in obj]
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="replace")
    raise TypeError(f"Not JSON-serializable: {obj!r} ({type(obj)})")


def canonical_json(obj) -> str:
    return json.dumps(normalize_for_json(obj), sort_keys=True, ensure_ascii=False)


def element_to_xml_str(elem: ET.Element) -> str:
    c = ET.fromstring(ET.tostring(elem, encoding="unicode"))
    ET.indent(c, space="  ")
    return ET.tostring(c, encoding="unicode", method="xml")


_TRANSLATION_STRFTIME_FMT = "%Y-%m-%dT%H:%M:%SZ"


@contextmanager
def fixed_translation_wall_clock(iso_z: str):
    """Force decoder init translationTime (time.strftime with no tuple) to a stable value."""

    orig = time_module.strftime

    def _sw(fmt, t=None):
        if t is None and fmt == _TRANSLATION_STRFTIME_FMT:
            return iso_z
        return orig(fmt, t)

    with mock.patch("time.strftime", _sw):
        yield


@contextmanager
def deterministic_uuids():
    state = {"n": 0}

    def next_uuid(prefix: str = "uuid.") -> str:
        state["n"] += 1
        i = state["n"]
        return f"{prefix}{i & 0xFFFFFFFF:08x}-0000-4000-8000-{i:012x}"

    with mock.patch.object(deu, "getUUID", side_effect=next_uuid):
        yield


def effective_xml_config_overrides(overrides: dict | None) -> dict:
    """Baseline matches repo defaults; prevents TRANSLATOR/TITLES leaking from other tests."""
    merged = {
        "TRANSLATOR": False,
        "TITLES": 0,
    }
    if overrides:
        merged.update(overrides)
    return merged


@contextmanager
def xml_config_overrides(overrides: dict | None):
    merged = effective_xml_config_overrides(overrides)
    saved = {}
    try:
        for k, v in merged.items():
            saved[k] = getattr(des, k, None)
            setattr(des, k, v)
        yield
    finally:
        for k, v in saved.items():
            setattr(des, k, v)


def make_encoder(product: str, geo_db: dict | None):
    if product == "METAR":
        from gifts.METAR import Encoder

        return Encoder(geo_db or {})
    if product == "TAF":
        from gifts.TAF import Encoder

        return Encoder(geo_db or {})
    if product == "TCA":
        from gifts.TCA import Encoder

        return Encoder()
    if product == "VAA":
        from gifts.VAA import Encoder

        return Encoder()
    if product == "SWA":
        from gifts.SWA import Encoder

        return Encoder()
    raise ValueError(f"Unknown product {product!r}")


def ahl_public_fields(enc, text: str) -> dict:
    m = enc.re_AHL.search(text)
    if not m:
        return {}
    d = m.groupdict("")
    d["tt"] = enc.T1T2
    return normalize_for_json(d)


def collect_reports(enc, text: str, receipt_time=None):
    """Run iter_encode_stages; return list of dicts tac, decoded, iwxxm_xml (may be None)."""
    if receipt_time is not None:
        stages = enc.iter_encode_stages(text, receiptTime=receipt_time)
    else:
        stages = enc.iter_encode_stages(text)
    reports = []
    for st in stages:
        el = st["element"]
        reports.append(
            {
                "tac": st["tac"],
                "decoded": normalize_for_json(st["decoded"]),
                "iwxxm_xml": element_to_xml_str(el) if el is not None else None,
            }
        )
    return reports


def _translation_wall_iso(freeze_t: str) -> str:
    s = freeze_t.strip()
    if s.endswith("Z"):
        return s
    if s.endswith("+00:00"):
        return s[:-6] + "Z"
    if "T" in s:
        return s + ("Z" if not s.endswith("Z") else "")
    return s


def _freeze_time_and_clock(case_spec: dict):
    """freezegun for date arithmetic + fixed strftime for decoder translationTime."""
    from freezegun import freeze_time

    freeze_t = case_spec["freeze_time"]
    wall = _translation_wall_iso(freeze_t)
    return freeze_time(freeze_t), fixed_translation_wall_clock(wall)


def build_case_document(case_spec: dict) -> dict:
    """Build full case.json payload under freezegun + deterministic UUID (caller wraps time)."""
    product = case_spec["product"]
    text = case_spec["input"]
    geo_db = case_spec.get("geo_db")
    overrides = case_spec.get("xml_config_overrides")
    effective = effective_xml_config_overrides(overrides)
    receipt_time = case_spec.get("receipt_time")

    with xml_config_overrides(overrides):
        ft, wall = _freeze_time_and_clock(case_spec)
        with ft:
            with wall:
                with deterministic_uuids():
                    enc = make_encoder(product, geo_db)
                    ahl = ahl_public_fields(enc, text)
                    reports = collect_reports(enc, text, receipt_time=receipt_time)

    val_ver = des.IWXXM_VALIDATOR_VERSION
    return {
        "schema": 1,
        "case_id": case_spec["case_id"],
        "product": product,
        "notes": case_spec.get("notes", ""),
        "freeze_time": case_spec["freeze_time"],
        "input": text,
        "geo_db": normalize_for_json(geo_db or {}),
        "xml_config_overrides": normalize_for_json(effective),
        "iwxxm_validator_version": val_ver,
        "validation_profile": {
            "tool": "iwxxmValidator.py",
            "recommended_argv": ["--noGMLChecks", "-v", val_ver, "<directory>"],
            "working_directory_relative": "validation",
            "description": "CRUX jar validates IWXXM XML (schema + Schematron); see validation/README.md",
        },
        "ahl": ahl,
        "reports": reports,
    }


def load_case_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pipeline_case_paths():
    base = repo_root() / "testdata" / "pipeline"
    if not base.is_dir():
        return []
    return sorted(p / "case.json" for p in base.iterdir() if p.is_dir() and (p / "case.json").is_file())


@contextmanager
def replay_determinism_for_case(case_data: dict):
    """Same stack as build_case_document: xml overrides from case + frozen time + UUID."""
    ft, wall = _freeze_time_and_clock({"freeze_time": case_data["freeze_time"]})
    with xml_config_overrides(case_data.get("xml_config_overrides")):
        with ft:
            with wall:
                with deterministic_uuids():
                    yield


def assert_reports_match(expected: list, actual: list):
    assert len(actual) == len(expected), f"Report count mismatch: {len(actual)} vs {len(expected)}"
    for i, (exp, got) in enumerate(zip(expected, actual)):
        assert exp["tac"] == got["tac"], f"tac mismatch at {i}"
        assert canonical_json(exp["decoded"]) == canonical_json(got["decoded"]), f"decoded mismatch at {i}"
        assert (exp.get("iwxxm_xml") or "") == (got.get("iwxxm_xml") or ""), f"iwxxm_xml mismatch at {i}"
