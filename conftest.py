import pytest

from cafebabel.core import app as myapp


def pytest_runtest_setup():
    from cli import _initdb
    _initdb()


def pytest_runtest_teardown():
    from cli import _dropdb
    _dropdb()


@pytest.fixture
def app():
    return myapp
