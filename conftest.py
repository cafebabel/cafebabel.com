import pytest

from flask_security.confirmable import confirm_user

from cli import _initdb
from cafebabel.core import app as myapp
from cafebabel.users.models import User


@pytest.fixture
def app():
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
