"""Tests for gifts.skyfield_support."""

import sys
from unittest import mock

from gifts import skyfield_support as ss


def test_ensure_creates_bsp_under_skyfield_path(tmp_path, monkeypatch):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    fake = mock.Mock()
    fake.__path__ = [str(pkg)]
    monkeypatch.setattr(ss, "_import_skyfield", lambda: fake)
    ss.ensure_skyfield_bsp_files()
    bsp = tmp_path / "pkg" / "bsp_files"
    assert bsp.is_dir()
    assert oct(bsp.stat().st_mode)[-3:] == "777"


def test_ensure_skips_when_dir_exists(tmp_path, monkeypatch):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "bsp_files").mkdir()
    fake = mock.Mock()
    fake.__path__ = [str(pkg)]
    monkeypatch.setattr(ss, "_import_skyfield", lambda: fake)
    ss.ensure_skyfield_bsp_files()
    assert (pkg / "bsp_files").is_dir()


def test_ensure_egg_fallback_creates_path(tmp_path, monkeypatch):
    site = tmp_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    site.mkdir(parents=True)
    egg = f"skyfield-1-py{sys.version_info.major}.{sys.version_info.minor}.egg"
    (site / egg).mkdir()
    (site / egg / "skyfield").mkdir()
    monkeypatch.setattr(ss.sys, "prefix", str(tmp_path))
    monkeypatch.setattr(ss, "_import_skyfield", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    ss.ensure_skyfield_bsp_files()
    assert (site / egg / "skyfield" / "bsp_files").is_dir()


def test_ensure_prints_when_no_skyfield_and_no_egg(tmp_path, monkeypatch, capsys):
    site = tmp_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    site.mkdir(parents=True)
    monkeypatch.setattr(ss.sys, "prefix", str(tmp_path))
    monkeypatch.setattr(ss, "_import_skyfield", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    ss.ensure_skyfield_bsp_files()
    out = capsys.readouterr().out
    assert "Unable to create bsp_files" in out


def test_ensure_prints_when_site_packages_missing(tmp_path, monkeypatch, capsys):
    """If sys.prefix has no site-packages dir, listdir would raise — must not crash."""
    # prefix exists but lib/pythonX.Y/site-packages is never created
    tmp_path.mkdir(exist_ok=True)
    monkeypatch.setattr(ss.sys, "prefix", str(tmp_path))
    monkeypatch.setattr(ss, "_import_skyfield", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    ss.ensure_skyfield_bsp_files()
    out = capsys.readouterr().out
    assert "Unable to create bsp_files" in out
