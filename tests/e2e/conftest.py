import os

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VALIDATION_ROOT = os.path.join(REPO_ROOT, "validation")


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end cross-service tests")


@pytest.fixture
def validation_dir():
    return VALIDATION_ROOT


@pytest.fixture
def has_crux(validation_dir):
    jar = os.path.join(validation_dir, "bin", "crux-1.3-all.jar")
    return os.path.isfile(jar)
