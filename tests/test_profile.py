from unittest import TestCase
from flask_security.confirmable import confirm_user

from auth import security  # noqa: to load the security extension.
from core.models import User, UserProfile
from cli import _initdb
from core import app


class ProfileTest(TestCase):
    def setUp(self):
        _initdb()

    def test_confirm_user_creates_profile(self):
        user = User.create(email='testy@tester.local', password='secret')
        with app.app_context():
            confirm_user(user)
        assert UserProfile.get(user=user)
