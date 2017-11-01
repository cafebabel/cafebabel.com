from flask_security.confirmable import confirm_user

from ..core.models import User, UserProfile


def test_confirm_user_creates_profile(app):
    user = User.create(email='testy@tester.local', password='secret')
    with app.app_context():
        confirm_user(user)
    assert UserProfile.get(user=user)
