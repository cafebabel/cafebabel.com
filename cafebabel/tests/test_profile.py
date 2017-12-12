from flask_security.confirmable import confirm_user

from .utils import login
from ..users.models import User


def test_confirm_user_creates_default_profile(app):
    user = User.objects.create(email='test_user@example.com',
                               password='secret')
    with app.app_context():
        confirm_user(user)
    assert user.profile.name == user.email


def test_user_profile_has_list_of_published_articles_no_draft(client, article):
    response = client.get(f'/profile/{article.author.id}/')
    assert response.status_code == 200
    assert article.title not in response


def test_author_profile_has_list_of_published_articles_and_drafts(
        client, user, article, published_article):
    login(client, user.email, 'secret')
    published_article.modify(author=user)
    response = client.get(f'/profile/', follow_redirects=True)
    assert response.status_code == 200
    assert article.title in response
    assert published_article.title in response
