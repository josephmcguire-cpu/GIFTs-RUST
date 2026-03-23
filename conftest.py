"""Repo-wide pytest hooks (rootdir)."""

from __future__ import annotations


def pytest_configure(config):
    import warnings

    # Avoid importing urllib3 here (import emits LibreSSL warning before filters apply).
    warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")
    warnings.filterwarnings("ignore", message="The NumPy module was reloaded")
