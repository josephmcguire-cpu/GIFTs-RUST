"""Unit tests for demo/iwxxmd (watchdog + daemon paths mocked)."""

import logging
import os
import pickle
import signal
from unittest import mock

import pytest

pytest.importorskip("watchdog")

import iwxxmd as m  # noqa: E402


def test_dow_file_handler_emit_rollover(tmp_path, monkeypatch):
    log = tmp_path / "base"
    h = m.DOWFileHandler(directory=str(tmp_path), basename="base")
    h.baseFilename = str(log) + "_Mon"
    h.stream = open(os.devnull, "w")
    rec = logging.LogRecord("n", logging.INFO, __file__, 1, "hi", None, None)

    real_strftime = m.time.strftime

    def fake_strftime(fmt, t=None):
        if "%a" in fmt and fmt.endswith("%a"):
            return "Tue"
        return real_strftime(fmt, t) if t is not None else real_strftime(fmt)

    monkeypatch.setattr(m.time, "strftime", fake_strftime)
    h.emit(rec)


def test_dispatcher_encodes_tac(tmp_path):
    from gifts.TCA import Encoder as TE

    enc = TE()
    d = m.Dispatcher(enc, delete_flag=False, header=False, outputDirectory=str(tmp_path))
    tac = """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
"""
    p = tmp_path / "x.txt"
    p.write_text(tac, encoding="utf-8")

    class Ev:
        is_directory = False
        src_path = str(p)

    d.on_closed(Ev())
    assert any(tmp_path.glob("*.xml"))


def test_dispatcher_delete_and_read_error(tmp_path, monkeypatch, caplog):
    from gifts.TCA import Encoder as TE

    enc = TE()
    d = m.Dispatcher(enc, delete_flag=True, header=False, outputDirectory=str(tmp_path))
    caplog.set_level(logging.ERROR)

    class Ev:
        is_directory = False
        src_path = str(tmp_path / "missing.txt")

    d.on_closed(Ev())
    assert "Unable to read" in caplog.text


def test_monitor_rejects_same_in_out(tmp_path):
    from gifts.TCA import Encoder as TE

    enc = TE()
    p = str(tmp_path)
    with pytest.raises(SystemExit):
        m.Monitor(enc, False, False, p, p)


def test_monitor_rejects_bad_input_dir(tmp_path):
    from gifts.TCA import Encoder as TE

    enc = TE()
    inp = tmp_path / "in"
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(SystemExit):
        m.Monitor(enc, False, False, str(inp), str(out))


def test_main_tca(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    for d in (inp, out, logs):
        d.mkdir()
    cfg = tmp_path / "cfg.ini"
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
    monkeypatch.setattr(m.Daemon, "start", lambda self: None)
    m.main(["iwxxmd.py", str(cfg)])


def test_main_metar_with_pickle_db(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    db = tmp_path / "db.pkl"
    for d in (inp, out, logs):
        d.mkdir()
    with open(db, "wb") as fh:
        pickle.dump({"BIAR": "x|y|z|0 0 0"}, fh)
    cfg = tmp_path / "cfg.ini"
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
    monkeypatch.setattr(m.Daemon, "start", lambda self: None)
    m.main(["iwxxmd.py", str(cfg)])


def test_daemonize_all_child_paths(monkeypatch):
    monkeypatch.setattr(os, "fork", lambda: 0)
    monkeypatch.setattr(os, "chdir", lambda p: None)
    monkeypatch.setattr(os, "setsid", lambda: None)
    monkeypatch.setattr(os, "umask", lambda m: None)
    monkeypatch.setattr(os, "dup2", lambda a, b: None)
    monkeypatch.setattr(m.sys.stdin, "fileno", lambda: 0)
    monkeypatch.setattr(m.sys.stdout, "fileno", lambda: 1)
    monkeypatch.setattr(m.sys.stderr, "fileno", lambda: 2)
    d = m.Daemon()
    d.daemonize()


def test_run_loop_exits(monkeypatch, tmp_path):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    for d in (inp, out, logs):
        d.mkdir()
    from gifts.TCA import Encoder as TE

    enc = TE()
    mon = m.Monitor(enc, False, False, str(inp), str(out))
    mon.observer = mock.Mock()
    mon.observer.is_alive.return_value = False
    monkeypatch.setattr(m.time, "sleep", mock.Mock(side_effect=StopIteration))
    with pytest.raises(StopIteration):
        mon.run()


def test_toggle_and_shutdown(monkeypatch, tmp_path):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    for d in (inp, out, logs):
        d.mkdir()
    from gifts.TCA import Encoder as TE

    enc = TE()
    mon = m.Monitor(enc, False, False, str(inp), str(out))
    mon.observer = mock.Mock()
    mon.logger = logging.getLogger("t")
    mon.logger.setLevel(logging.INFO)
    mon.toggleLoggingLevel(signal.SIGUSR1, None)
    with pytest.raises(SystemExit):
        mon.shutdown(signal.SIGTERM, None)
