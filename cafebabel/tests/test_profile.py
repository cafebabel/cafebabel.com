from flask_security.confirmable import confirm_user

from ..users.models import User, UserProfile


def test_confirm_user_creates_profile(app):
    user = User(email='test_user@example.com', password='secret').save()
    with app.app_context():
        confirm_user(user)
    assert UserProfile.objects.get(user=user)
