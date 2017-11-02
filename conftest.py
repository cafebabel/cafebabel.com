import pytest
from flask_security.confirmable import confirm_user

from cafebabel import app as myapp
from cafebabel.core.commands import _dropdb, _initdb
from cafebabel.users.models import User


def pytest_runtest_setup():
    _initdb()


def pytest_runtest_teardown():
    _dropdb()


@pytest.fixture
def app():
    from cafebabel import app as myapp
    return myapp


@pytest.fixture
def user():
    _initdb()
    user = User.create(email='testy@tester.local', password='secret')
    with myapp.app_context():
        confirm_user(user)
    return user


@pytest.fixture
def admin():
    _initdb()
    return User.get(email='admin@example.com')
