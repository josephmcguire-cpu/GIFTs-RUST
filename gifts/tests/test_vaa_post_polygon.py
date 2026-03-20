"""Direct tests for vaaDecoder.Decoder.postPolygon and related helpers."""

import logging

import pytest

from gifts import vaaDecoder


@pytest.fixture
def dec():
    d = vaaDecoder.Decoder()
    d._Logger = logging.getLogger("test")
    return d


def test_post_polygon_none(dec):
    dec.postPolygon(None)


def test_post_polygon_closes_open_ring(dec):
    cloudInfo = {"pnts": ["10.0 20.0", "11.0 21.0"]}
    dec.postPolygon(cloudInfo)
    assert cloudInfo["pnts"][0] == cloudInfo["pnts"][-1]


def test_post_polygon_box_nm(dec):
    cloudInfo = {
        "box": {"width": "20", "uom": "NM"},
        "pnts": ["0.0 10.0", "1.0 11.0", "0.0 10.0"],
    }
    dec.postPolygon(cloudInfo)
    assert isinstance(cloudInfo["pnts"], list)
    assert cloudInfo["pnts"][0] == cloudInfo["pnts"][-1]


def test_post_polygon_box_km(dec):
    cloudInfo = {
        "box": {"width": "20", "uom": "KM"},
        "pnts": ["0.0 10.0", "1.0 11.0", "0.0 10.0"],
    }
    dec.postPolygon(cloudInfo)


def test_post_polygon_keyerror_swallowed(dec):
    cloudInfo = {"pnts": []}
    dec.postPolygon(cloudInfo)


def test_rmk(dec):
    dec.vaa = {"remarks": None}
    dec.rmk("RMK: hello world")


def test_noash(dec):
    dec.vaa = {"clouds": {0: {"cldLyrs": []}}}
    dec._fhr = 0
    dec.lexer = mock_lexer("NIL")
    dec.noash()


def mock_lexer(name):
    class L:
        cur_token = type("T", (), {"name": name})()

    return L()


def test_vanotid_minimal(dec):
    dec.vaa = {"clouds": {0: {"cldLyrs": []}}}
    dec._fhr = 0
    dec._cloud = {"x": 1}
    dec.lexer = mock_lexer("NIL")
    # No wind pattern match — still exercises loop exit
    dec.vanotid("   ")
