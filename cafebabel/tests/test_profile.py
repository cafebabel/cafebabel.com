from flask_security.confirmable import confirm_user

from ..users import security  # noqa: to load the security extension.
from ..users.models import User, UserProfile
from cli import _initdb, _dropdb


def test_confirm_user_creates_profile(app):
    _initdb()
    user = User.create(email='testy@tester.local', password='secret')
    with app.app_context():
        confirm_user(user)
    assert UserProfile.get(user=user)
    _dropdb()
