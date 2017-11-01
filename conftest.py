import pytest
from cafebabel.core.commands import _dropdb, _initdb


def pytest_runtest_setup():
    _initdb()


def pytest_runtest_teardown():
    _dropdb()


@pytest.fixture
def app():
    from cafebabel import app as myapp
    return myapp
