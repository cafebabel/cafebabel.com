import pytest
from flask_security.confirmable import confirm_user

from ..auth import security  # noqa: to load the security extension.
from ..core import app as myapp
from ..core.models import User, UserProfile


@pytest.fixture
def app():
    return myapp


def test_confirm_user_creates_profile(app):
    user = User.create(email='testy@tester.local', password='secret')
    with app.app_context():
        confirm_user(user)
    assert UserProfile.get(user=user)
