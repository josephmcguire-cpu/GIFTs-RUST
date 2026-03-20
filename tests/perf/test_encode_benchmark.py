"""Performance hooks (run with `pytest -m perf --benchmark-only`)."""

import pytest

from gifts.METAR import Encoder as ME

pytestmark = pytest.mark.perf


@pytest.fixture
def geo_db():
    return {"BIAR": "AKUREYRI|AEY|AKI|65.67 -18.07 27"}


def test_metar_encode_benchmark(benchmark, geo_db):
    text = """SAXX99 XXXX 151200
METAR BIAR 290000Z 33003KT 280V010 9999 OVC032 04/M00 Q1023=
"""
    enc = ME(geo_db)

    def run():
        enc.encode(text)

    benchmark(run)
