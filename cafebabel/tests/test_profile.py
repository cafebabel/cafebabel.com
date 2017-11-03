from flask_security.confirmable import confirm_user

from ..users.models import User


def test_confirm_user_creates_default_profile(app):
    user = User.objects.create(email='test_user@example.com',
                               password='secret')
    with app.app_context():
        confirm_user(user)
    assert user.profile.name == user.email
