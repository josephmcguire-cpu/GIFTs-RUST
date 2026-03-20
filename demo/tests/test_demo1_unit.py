"""Tests for demo1 helpers (Tk mocked)."""

from unittest import mock

import pytest

pytest.importorskip("tkinter")


def test_text_handler_emit_schedules_append():
    from demo1 import TextHandler

    widget = mock.Mock()
    widget.after = mock.Mock(side_effect=lambda delay, fn: fn())
    widget.configure = mock.Mock()
    widget.insert = mock.Mock()
    widget.yview = mock.Mock()
    h = TextHandler(widget)
    import logging

    record = logging.LogRecord("n", logging.INFO, __file__, 1, "hello", None, None)
    h.emit(record)
    widget.insert.assert_called()


@mock.patch("demo1.simpleGUI.__init__", lambda self: None)
def test_simplegui_class_exists():
    import demo1

    assert hasattr(demo1, "simpleGUI")
