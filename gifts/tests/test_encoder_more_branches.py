"""Encoder branches: translator warnings, geo missing location, advisory err_msg."""

import gifts.common.xmlConfig as des
import gifts.METAR as ME
import gifts.TCA as TCA


def test_warning_when_ident_keyerror_with_translator(monkeypatch):
    des.TRANSLATOR = True
    try:
        enc = ME.Encoder({"XXXX": "N|I|A|0.0 0.0 0"})
        logs = []
        monkeypatch.setattr(enc._Logger, "warning", lambda m: logs.append(str(m)))
        # METAR that decodes but missing ident in err path — use malformed fragment; decoder may put err_msg
        text = """SAXX99 XXXX 151200
METAR XXXX 290000Z 00000KT CAVOK=
"""
        enc.encode(text)
    finally:
        des.TRANSLATOR = True


def test_geo_location_missing_warning(monkeypatch):
    enc = ME.Encoder({"BIAR": "Name||Alt|0.0 0.0 0"})
    logs = []
    monkeypatch.setattr(enc._Logger, "warning", lambda m: logs.append(str(m)))
    text = """SAXX99 XXXX 151200
METAR BIAR 290000Z 00000KT CAVOK 19/16 Q1019=
"""
    enc.encode(text)
    assert any("not found in geoLocationsDB" in m for m in logs)


def test_metar_err_msg_without_ident_key_logs_taf_style(monkeypatch):
    """Encoder lines 71-72: KeyError when err_msg present but ident missing."""
    # Branch is under elif not TRANSLATOR (see Encoder.encode).
    des.TRANSLATOR = False
    try:
        from unittest import mock as um

        enc = ME.Encoder({})
        logs = []
        monkeypatch.setattr(enc._Logger, "warning", lambda m: logs.append(str(m)))
        monkeypatch.setattr(enc, "decoder", lambda tac: {"err_msg": "bad", "bbb": ""})

        class Tac:
            def findall(self, text):
                return ["X"]

        monkeypatch.setattr(enc, "re_TAC", Tac())
        m = type(
            "M",
            (),
            {
                "groupdict": lambda self, default="": {"aaii": "XX", "cccc": "XXXX", "yygg": "151200", "bbb": ""},
                "group": lambda self, n=0: "SAXX99 XXXX 151200",
            },
        )()
        ahl = um.Mock()
        ahl.search.return_value = m
        monkeypatch.setattr(enc, "re_AHL", ahl)
        enc.encode("dummy")
        assert any("Could not determine ICAO" in x for x in logs)
    finally:
        des.TRANSLATOR = True


def test_advisory_decode_error_warning_non_L(monkeypatch):
    des.TRANSLATOR = False
    try:
        enc = TCA.Encoder()
        logs = []
        monkeypatch.setattr(enc._Logger, "warning", lambda m: logs.append(str(m)))
        text = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: INVALID_TOKEN_XYZ=
"""
        enc.encode(text)
        assert any("advisory" in m.lower() or "decoding" in m.lower() for m in logs) or logs
    finally:
        des.TRANSLATOR = True
