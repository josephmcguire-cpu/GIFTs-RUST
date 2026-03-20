"""Unit tests for gifts.common.xmlUtilities."""

import os
import time

import pytest

from gifts.common import xmlUtilities as xu


def test_parseCodeRegistryTables_reads_nil(tmp_path):
    src = os.path.join(os.path.dirname(__file__), "..", "data")
    src = os.path.normpath(src)
    codes = xu.parseCodeRegistryTables(src, ["nil"])
    assert "nil" in codes
    assert isinstance(codes["nil"], dict)


def test_fix_date_future_month_decrements(monkeypatch):
    """If parsed time is far in the future, month rolls back."""
    tms = [2035, 6, 15, 12, 0, 0, 0, 0, -1]
    monkeypatch.setattr(xu.time, "time", lambda: time.mktime((2020, 1, 1, 0, 0, 0, 0, 0, -1)))
    xu.fix_date(tms)
    assert tms[1] == 5


def test_fix_date_past_month_increments(monkeypatch):
    tms = [2020, 1, 15, 12, 0, 0, 0, 0, -1]
    monkeypatch.setattr(xu.time, "time", lambda: time.mktime((2020, 2, 20, 0, 0, 0, 0, 0, -1)))
    xu.fix_date(tms)
    assert tms[1] == 2


def test_is_a_number():
    assert xu.is_a_number("3")
    assert xu.is_a_number("-3.5")
    assert not xu.is_a_number("x")


def test_getUUID():
    assert xu.getUUID().startswith("uuid.")


def test_computeLatLon_wraps():
    s = xu.computeLatLon(0.0, 179.0, 90, 100.0)
    assert " " in s


def test_checkVisibility_units_and_branches():
    assert xu.checkVisibility("1000") == "1000"
    assert xu.checkVisibility(950) == 900
    assert xu.checkVisibility(8500) == 8000
    assert xu.checkVisibility(9990) == 9000
    assert xu.checkVisibility(1, uom="[mi_i]") != "1"
    assert xu.checkVisibility(10, uom="[ft_i]") != "10"


def test_checkRVR_branches():
    assert xu.checkRVR(300) == 300
    assert xu.checkRVR(425) == 400
    assert xu.checkRVR(900) == 900
    assert xu.checkRVR("100") == "100"


def test_computeArea_and_ccw():
    with pytest.raises(ValueError):
        xu.computeArea([(0, 0), (1, 0)])
    poly_open = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
    a = xu.computeArea(poly_open)
    assert isinstance(a, float)
    assert isinstance(xu.isCCW(poly_open), bool)
