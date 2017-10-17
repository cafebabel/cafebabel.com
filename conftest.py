import pytest

from cafebabel.core import app as myapp


@pytest.fixture
def app():
    return myapp
