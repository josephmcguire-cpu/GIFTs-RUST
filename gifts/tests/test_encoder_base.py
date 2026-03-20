"""Branch coverage for gifts.common.Encoder base class."""

import gifts.common.xmlConfig as des
import gifts.METAR as ME


def test_encode_no_ahl_returns_empty_bulletin():
    enc = ME.Encoder({"XXXX": "|||0.0 0.0 0"})
    out = enc.encode("no ahl line here")
    assert len(out) == 0


def test_encode_skips_tac_when_translator_off_and_err_msg(monkeypatch):
    enc = ME.Encoder({"USTR": "N|I|A|0 0 0"})
    des.TRANSLATOR = False
    try:
        text = """SAXX99 XXXX 151200
METAR USTR 311938Z REMARKS INVALID=
"""
        out = enc.encode(text)
        assert len(out) == 0
    finally:
        des.TRANSLATOR = True


def test_geo_get_raises_keyerror_skipped(monkeypatch):
    class BadDB:
        def get(self, key, default=None):
            raise KeyError("x")

    enc = ME.Encoder(BadDB())
    text = """SAXX99 XXXX 151200
METAR USTR 290000Z 00000KT CAVOK 19/16 Q1019=
"""
    cap = []

    def warn(msg):
        cap.append(msg)

    monkeypatch.setattr(enc._Logger, "warning", warn)
    out = enc.encode(text)
    assert len(out) == 0
    assert any("icaoID" in str(m) for m in cap)


def test_encoder_syntax_error_in_append_logged(monkeypatch):
    enc = ME.Encoder({"USTR": "N|I|A|61.33 73.42 44"})

    def boom(*a, **k):
        raise SyntaxError("bad xml")

    monkeypatch.setattr(enc, "encoder", boom)
    text = """SAXX99 XXXX 151200
METAR USTR 290000Z 00000KT CAVOK 19/16 Q1019=
"""
    logs = []
    monkeypatch.setattr(enc._Logger, "warning", lambda m: logs.append(m))
    enc.encode(text)
    assert logs
