from flask_security.confirmable import confirm_user

from .utils import login
from ..users.models import User


def test_confirm_user_creates_default_profile(app):
    user = User.objects.create(email='test_user@example.com',
                               password='secret')
    with app.app_context():
        confirm_user(user)
    assert user.profile.name == user.email


def test_author_profile_has_no_list_of_drafts(client, user, article):
    login(client, user.email, 'secret')
    response = client.get(f'/profile/{user.id}/')
    assert response.status_code == 200
    assert article.title not in response.get_data(as_text=True)


def test_author_profile_has_list_of_published_articles(client, user, article):
    login(client, user.email, 'secret')
    article.status = 'published'
    article.author = user
    article.save()
    response = client.get(f'/profile/{user.id}/')
    assert response.status_code == 200
    assert article.title in response.get_data(as_text=True)
