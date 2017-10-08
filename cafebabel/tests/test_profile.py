from unittest import TestCase

from peewee import drop_model_tables, create_model_tables
from flask_security.confirmable import confirm_user

from ..core.models import User, UserProfile
from ..core import app


class UserProfileTest(TestCase):
    def setUp(self):
        app.testing = True

    def tearDown(self):
        tables = [User, UserProfile]
        drop_model_tables(tables, fail_silently=True)
        create_model_tables(tables, fail_silently=True)

    @app.app_context
    def test_confirm_user_creates_profile(self):
        user = User.create(email='testy@tester.local', password='secret')
        confirm_user(user)
        assert UserProfile.get(user=user)
