"""Extra coverage for gifts.common.bulletin: __str__, write edge cases."""

import os

import pytest

import gifts.common.bulletin as bulletin
from gifts.TCA import Encoder as TE


def test_bulletin_str_returns_pretty_xml():
    enc = TE()
    tac = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
"""
    b = enc.encode(tac)
    s = str(b)
    assert "MeteorologicalBulletin" in s
    assert b.bulletin is None


def test_write_raises_on_bad_object_type():
    enc = TE()
    tac = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
"""
    b = enc.encode(tac)
    with pytest.raises(IOError):
        b.write(42)


def test_write_typeerror_fallback_on_tree_write(monkeypatch, tmp_path):
    enc = TE()
    tac = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
"""
    b = enc.encode(tac)

    _orig = bulletin.ET.ElementTree.write
    calls = [0]

    def write_maybe(self, *a, **k):
        calls[0] += 1
        if calls[0] == 1:
            raise TypeError("no short_empty_elements")
        return _orig(self, *a, **k)

    monkeypatch.setattr(bulletin.ET.ElementTree, "write", write_maybe)
    fh = open(os.devnull, "wb")
    b.write(fh)
    fh.close()


def test_write_compress_without_gzip_raises(monkeypatch, tmp_path):
    enc = TE()
    tac = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
"""
    b = enc.encode(tac)
    monkeypatch.delitem(bulletin.__dict__, "gzip", raising=False)
    with pytest.raises(SystemError):
        b.write(tmp_path, compress=True)


def test_iswriteable_false_for_plain_object():
    b = bulletin.Bulletin()
    assert b._iswriteable(object()) is False


def test_str_raises_when_bulletin_id_invalid():
    enc = TE()
    tac = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
"""
    b = enc.encode(tac)
    b._bulletinId = "INVALID"
    with pytest.raises(bulletin.XMLError):
        str(b)
