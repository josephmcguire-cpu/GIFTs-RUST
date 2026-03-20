"""Cover demo1.simpleGUI paths with Tk and I/O mocked."""

import pickle
from unittest import mock

import pytest

pytest.importorskip("tkinter")


def _make_gui(monkeypatch, tmp_path):
    import demo1

    db = tmp_path / "aerodromes.db"
    db.write_bytes(pickle.dumps({"BIAR": "AKUREYRI|AEY|AKI|65.67 -18.07 27"}))
    monkeypatch.chdir(tmp_path)

    win = mock.Mock()
    win.title = mock.Mock()
    win.rowconfigure = mock.Mock()
    win.mainloop = mock.Mock()

    ent_tac = mock.MagicMock()
    ent_xml = mock.MagicMock()
    n = {"k": 0}

    def entry_factory(*a, **k):
        n["k"] += 1
        return ent_tac if n["k"] == 1 else ent_xml

    with (
        mock.patch.object(demo1.tk, "Tk", return_value=win),
        mock.patch.object(demo1, "scrolledtext") as st,
        mock.patch.object(demo1.tk, "Frame", return_value=mock.Mock()),
        mock.patch.object(demo1.tk, "Button", side_effect=lambda *a, **k: mock.MagicMock()),
        mock.patch.object(demo1.tk, "Entry", side_effect=entry_factory),
        mock.patch.object(demo1.tk, "Label", return_value=mock.Mock()),
    ):
        st.ScrolledText.return_value = mock.MagicMock()
        gui = demo1.simpleGUI()
    return gui


def test_encode_metar_writes_bulletin(tmp_path, monkeypatch):
    gui = _make_gui(monkeypatch, tmp_path)
    tac = tmp_path / "t.txt"
    tac.write_text(
        """SAXX99 XXXX 151200
METAR BIAR 290000Z 33003KT 280V010 9999 OVC032 04/M00 Q1023=
""",
        encoding="utf-8",
    )
    gui.ent_tac.get.return_value = str(tac)
    gui.logger = mock.Mock()
    gui.encode()
    gui.ent_xml.insert.assert_called()
    gui.logger.info.assert_called()


def test_encode_no_ahl_match(tmp_path, monkeypatch):
    gui = _make_gui(monkeypatch, tmp_path)
    tac = tmp_path / "t.txt"
    tac.write_text("no ahl here\n", encoding="utf-8")
    gui.ent_tac.get.return_value = str(tac)
    gui.logger = mock.Mock()
    gui.encode()
    gui.logger.error.assert_called()


def test_encode_tca_advisory_message(tmp_path, monkeypatch):
    gui = _make_gui(monkeypatch, tmp_path)
    tac = tmp_path / "t.txt"
    tac.write_text(
        """FKNT23 KNHC 111800
TC ADVISORY
STATUS: TEST=
""",
        encoding="utf-8",
    )
    gui.ent_tac.get.return_value = str(tac)
    gui.logger = mock.Mock()
    gui.encode()
    assert gui.logger.info.called


def test_open_file_cancel(tmp_path, monkeypatch):
    import demo1

    gui = _make_gui(monkeypatch, tmp_path)
    with mock.patch.object(demo1, "askopenfilename", return_value=""):
        assert gui.open_file() is None


def test_open_file_sets_path(tmp_path, monkeypatch):
    import demo1

    gui = _make_gui(monkeypatch, tmp_path)
    with mock.patch.object(demo1, "askopenfilename", return_value=str(tmp_path / "x.txt")):
        r = gui.open_file()
    gui.ent_tac.delete.assert_called()
    gui.ent_tac.insert.assert_called()
    assert r == "break"


def test_clear_fields(tmp_path, monkeypatch):
    gui = _make_gui(monkeypatch, tmp_path)
    gui.clear_fields()
    gui.ent_tac.delete.assert_called()
    gui.ent_xml.delete.assert_called()


def test_windows_branch_loads_win_db(tmp_path, monkeypatch):
    import demo1

    db = tmp_path / "aerodromes.win.db"
    db.write_bytes(pickle.dumps({"W": "a|b|c|0 0 0"}))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(demo1.platform, "system", lambda: "Windows")
    win = mock.Mock()
    with (
        mock.patch.object(demo1.tk, "Tk", return_value=win),
        mock.patch.object(demo1, "scrolledtext") as st,
        mock.patch.object(demo1.tk, "Frame", return_value=mock.Mock()),
        mock.patch.object(demo1.tk, "Button", side_effect=lambda *a, **k: mock.MagicMock()),
        mock.patch.object(demo1.tk, "Entry", side_effect=lambda *a, **k: mock.MagicMock()),
        mock.patch.object(demo1.tk, "Label", return_value=mock.Mock()),
    ):
        st.ScrolledText.return_value = mock.MagicMock()
        demo1.simpleGUI()
