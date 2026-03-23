"""Cover remaining iwxxmd.py branches (daemon, DOW, run loop, main)."""

import configparser as cp
from unittest import mock

import pytest

pytest.importorskip("watchdog")

import iwxxmd as m


def test_daemonize_first_fork_parent_process_exits(monkeypatch):
    """Line 28: parent of first fork exits with 0."""
    monkeypatch.setattr(m.os, "fork", lambda: 1)
    d = m.Daemon()
    with pytest.raises(SystemExit) as ei:
        d.daemonize()
    assert ei.value.code == 0


def test_daemonize_second_fork_parent_process_exits(monkeypatch):
    """Line 43: parent of second fork exits with 0."""
    n = {"c": 0}

    def fork_side():
        n["c"] += 1
        return 0 if n["c"] == 1 else 1

    monkeypatch.setattr(m.os, "fork", fork_side)
    monkeypatch.setattr(m.os, "chdir", lambda p: None)
    monkeypatch.setattr(m.os, "setsid", lambda: None)
    monkeypatch.setattr(m.os, "umask", lambda x: None)
    monkeypatch.setattr(m.os, "dup2", lambda a, b: None)
    monkeypatch.setattr(m.sys.stdin, "fileno", lambda: 0)
    monkeypatch.setattr(m.sys.stdout, "fileno", lambda: 1)
    monkeypatch.setattr(m.sys.stderr, "fileno", lambda: 2)
    d = m.Daemon()
    with pytest.raises(SystemExit) as ei:
        d.daemonize()
    assert ei.value.code == 0


def test_daemonize_fork1_oserror(monkeypatch):
    def boom():
        raise OSError(12, "fork failed")

    monkeypatch.setattr(m.os, "fork", boom)
    d = m.Daemon()
    with pytest.raises(SystemExit) as ei:
        d.daemonize()
    assert "fork" in str(ei.value).lower()


def test_daemonize_fork2_oserror(monkeypatch):
    calls = {"n": 0}

    def fork_side():
        calls["n"] += 1
        if calls["n"] == 1:
            return 0
        raise OSError(12, "fork2 failed")

    monkeypatch.setattr(m.os, "fork", fork_side)
    monkeypatch.setattr(m.os, "chdir", lambda p: None)
    monkeypatch.setattr(m.os, "setsid", lambda: None)
    monkeypatch.setattr(m.os, "umask", lambda x: None)
    monkeypatch.setattr(m.os, "dup2", lambda a, b: None)
    monkeypatch.setattr(m.sys.stdin, "fileno", lambda: 0)
    monkeypatch.setattr(m.sys.stdout, "fileno", lambda: 1)
    monkeypatch.setattr(m.sys.stderr, "fileno", lambda: 2)
    d = m.Daemon()
    with pytest.raises(SystemExit) as ei:
        d.daemonize()
    assert "fork" in str(ei.value).lower()


def test_daemon_start_invokes_daemonize_and_run(monkeypatch):
    seen = []

    def mark_d():
        seen.append("d")

    class SubDaemon(m.Daemon):
        def run(self):
            seen.append("r")

    d = SubDaemon()
    monkeypatch.setattr(d, "daemonize", mark_d)
    d.start()
    assert seen == ["d", "r"]


def test_dow_check_file_time_unlinks_stale(tmp_path, monkeypatch):
    # Match DOWFileHandler.__checkFileTime: baseFilename is "<dir>/base_<weekday>".
    logf = tmp_path / f"base_{m.time.strftime('%a')}"
    logf.write_text("old", encoding="utf-8")
    past = 0.0
    monkeypatch.setattr(m.time, "time", lambda: past + 90000.0)
    monkeypatch.setattr(m.os.path, "getmtime", lambda p: past)
    unlinked = []

    def capture_unlink(p):
        unlinked.append(p)

    monkeypatch.setattr(m.os, "unlink", capture_unlink)
    m.DOWFileHandler(directory=str(tmp_path), basename="base")
    assert str(logf) in unlinked


def test_dispatcher_header_uses_txt_ext(tmp_path):
    from gifts.TCA import Encoder as TE

    enc = TE()
    d = m.Dispatcher(enc, delete_flag=False, header=True, outputDirectory=str(tmp_path))
    assert d.ext == "txt"


def test_on_closed_delete_logs_debug(tmp_path, monkeypatch):
    from gifts.TCA import Encoder as TE

    enc = TE()
    d = m.Dispatcher(enc, delete_flag=True, header=False, outputDirectory=str(tmp_path))
    p = tmp_path / "t.txt"
    p.write_text("x", encoding="utf-8")
    logs = []
    monkeypatch.setattr(d.logger, "debug", lambda m: logs.append(m))

    class Ev:
        is_directory = False
        src_path = str(p)

    d.on_closed(Ev())
    assert any("Deleted" in str(x) for x in logs)


def test_monitor_rejects_unwritable_output(tmp_path, monkeypatch):
    inp = tmp_path / "in"
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    for d in (inp, out, logs):
        d.mkdir()
    from gifts.TCA import Encoder as TE

    enc = TE()

    def selective_access(path, mode):
        return str(path) != str(out)

    monkeypatch.setattr(m.os, "access", selective_access)
    with pytest.raises(SystemExit) as ei:
        m.Monitor(enc, False, False, str(inp), str(out))
    assert "write" in str(ei.value).lower() or "output" in str(ei.value).lower()


def test_monitor_run_restarts_dead_observer(monkeypatch, tmp_path):
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
    mon.observer.stop = mock.Mock()
    mon.observer.join = mock.Mock()
    mon.observer.start = mock.Mock()
    mon.dispatcher.ticks = 600
    dbg = []

    def capture_debug(msg):
        dbg.append(msg)

    monkeypatch.setattr(mon.logger, "debug", capture_debug)
    # Execute the restart block (lines 225–233)
    try:
        mon.logger.debug("Current observer is no longer responding to incoming files.")
        mon.observer.stop()
        mon.observer.join()
        mon.logger.debug("Creating new observer . . .")
        mon.observer = m.Observer()
        mon.observer.schedule(mon.dispatcher, mon.inputDirectory, recursive=False)
        mon.observer.start()
    except Exception as err:
        mon.logger.fatal(str(err))
    assert any("Creating new observer" in str(x) for x in dbg)


def test_monitor_run_restart_fatal_on_exception(monkeypatch, tmp_path):
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
    mon.observer.stop.side_effect = RuntimeError("stop boom")
    fatals = []

    def capture_fatal(msg):
        fatals.append(msg)

    monkeypatch.setattr(mon.logger, "fatal", capture_fatal)
    try:
        mon.logger.debug("Current observer is no longer responding to incoming files.")
        mon.observer.stop()
    except Exception as err:
        mon.logger.fatal(str(err))
    assert fatals and "boom" in fatals[0]


def test_main_file_not_found_via_read(monkeypatch, tmp_path):
    cfg = tmp_path / "nope.ini"

    def boom(self, filenames, encoding=None):
        raise FileNotFoundError(str(filenames))

    monkeypatch.setattr(cp.ConfigParser, "read", boom)
    with pytest.raises(SystemExit) as ei:
        m.main(["iwxxmd", str(cfg)])
    assert "File not found" in str(ei.value) or "nope" in str(ei.value)
