"""iwxxmd.main() error paths and edge cases."""

import configparser
import pickle
from unittest import mock

import pytest

pytest.importorskip("watchdog")

import iwxxmd as m


def test_main_no_config_arg(monkeypatch):
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd"])
    assert "first argument" in str(ei.value)


def test_main_config_not_found():
    """ConfigParser.read does not raise for a missing path; empty read triggers Unrecognized."""
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", "/this/path/does/not/exist/iwxxmd.cfg"])
    assert "Unrecognized" in str(ei.value)


def test_main_unreadable_config(tmp_path, monkeypatch):
    cfg = tmp_path / "bad.ini"
    cfg.write_text("[[[broken", encoding="utf-8")
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", str(cfg)])
    assert "Error parsing" in str(ei.value) or "parsing" in str(ei.value).lower()


def test_main_empty_config_file_exists_but_no_sections(tmp_path):
    cfg = tmp_path / "empty.ini"
    cfg.write_text("", encoding="utf-8")
    with pytest.raises(configparser.NoSectionError):
        m.main(["iwxxmd", str(cfg)])


def test_main_bad_product(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    for d in (inp, out, logs):
        d.mkdir()
    cfg = tmp_path / "c.ini"
    cfg.write_text(
        f"""[internals]
product = not_a_product
delete_after_read = false
wmo_ahl_line = false
[directories]
input = {inp}
output = {out}
logs = {logs}
"""
    )
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", str(cfg)])
    assert "not one of" in str(ei.value)


def test_main_pickle_load_fails(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    db = tmp_path / "bad.pkl"
    for d in (inp, out, logs):
        d.mkdir()
    db.write_bytes(b"not a pickle")
    cfg = tmp_path / "c.ini"
    cfg.write_text(
        f"""[internals]
product = metar
delete_after_read = false
wmo_ahl_line = false
geo_locations_file = {db}
[directories]
input = {inp}
output = {out}
logs = {logs}
"""
    )
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", str(cfg)])
    assert str(ei.value)


def test_main_bad_log_directory(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    db = tmp_path / "db.pkl"
    db.write_bytes(pickle.dumps({"X": "a|b|c|0 0 0"}))
    for d in (inp, out):
        d.mkdir()
    cfg = tmp_path / "c.ini"
    cfg.write_text(
        f"""[internals]
product = metar
delete_after_read = false
wmo_ahl_line = false
geo_locations_file = {db}
[directories]
input = {inp}
output = {out}
logs = {tmp_path / "nologs"}
"""
    )
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", str(cfg)])
    assert "logs" in str(ei.value).lower() or "exist" in str(ei.value).lower()


def test_main_monitor_constructor_raises(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    for d in (inp, out, logs):
        d.mkdir()
    cfg = tmp_path / "c.ini"
    cfg.write_text(
        f"""[internals]
product = tca
delete_after_read = false
wmo_ahl_line = false
[directories]
input = {inp}
output = {out}
logs = {logs}
"""
    )

    def boom(*a, **k):
        raise RuntimeError("monitor boom")

    monkeypatch.setattr(m, "Monitor", boom)
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", str(cfg)])
    assert "monitor boom" in str(ei.value)


def test_dispatcher_encode_exception_logged(tmp_path, monkeypatch):
    """Encoder failure path uses logger.exception; avoid caplog (dictConfig in main() drops caplog handlers)."""
    from gifts.TCA import Encoder as TE

    enc = TE()
    d = m.Dispatcher(enc, False, False, str(tmp_path))
    p = tmp_path / "x.txt"
    p.write_text("garbage", encoding="utf-8")

    class Ev:
        is_directory = False
        src_path = str(p)

    with mock.patch.object(enc, "encode", side_effect=ValueError("boom")):
        with mock.patch.object(d.logger, "exception") as exc_log:
            d.on_closed(Ev())
    exc_log.assert_called_once()
    msg = exc_log.call_args[0][0]
    assert "Unable to convert" in msg and str(p) in msg


def test_dow_handler_rollover_old_file(tmp_path, monkeypatch):
    import time

    old = tmp_path / "base_Mon"
    old.write_text("x", encoding="utf-8")
    past = time.time() - 90000
    import os

    os.utime(old, (past, past))

    h = m.DOWFileHandler(directory=str(tmp_path), basename="base")
    h.baseFilename = str(old)
    h.stream = open(os.devnull, "w")
    rec = __import__("logging").LogRecord("n", 20, __file__, 1, "hi", None, None)
    h.emit(rec)
