from flask import current_app
from flask_security.confirmable import confirm_user
from http import HTTPStatus

from .utils import login
from ..users.models import User


def test_confirm_user_creates_default_profile(app):
    user = User.objects.create(email='test_user@example.com',
                               password='password')
    with app.app_context():
        confirm_user(user)
    assert user.profile.name == 'Anonymous'


def test_user_profile_has_button_to_full_list(client, article):
    response = client.get(f'/en/profile/{article.authors[0].id}/')
    assert response.status_code == HTTPStatus.OK
    assert 'See all articles and translations' in response


def test_user_profile_full_has_no_button_to_list(client, article):
    response = client.get(f'/en/profile/{article.authors[0].id}/?full')
    assert response.status_code == HTTPStatus.OK
    assert 'See all articles and translations' not in response


def test_user_profile_has_list_of_published_articles_no_draft(
        client, article, published_article):
    response = client.get(f'/en/profile/{article.authors[0].id}/')
    assert response.status_code == HTTPStatus.OK
    assert article.detail_url not in response
    assert published_article.detail_url in response


def test_user_profile_has_list_of_published_translations_no_draft(
        client, translation, published_translation):
    response = client.get(f'/en/profile/{translation.authors[0].id}/')
    assert response.status_code == HTTPStatus.OK
    assert translation.detail_url not in response
    assert published_translation.detail_url in response


def test_author_profile_has_list_of_published_articles_and_drafts(
        client, user, article, published_article):
    login(client, user.email, 'password')
    response = client.get(f'/en/profile/{article.authors[0].id}/')
    assert response.status_code == HTTPStatus.OK
    assert article.detail_url in response
    assert published_article.detail_url in response


def test_author_profile_has_list_of_published_translations_and_drafts(
        client, user, translation, published_translation):
    login(client, user.email, 'password')
    response = client.get(f'/en/profile/{translation.authors[0].id}/')
    assert response.status_code == HTTPStatus.OK
    assert translation.detail_url in response
    assert published_translation.detail_url in response


def test_author_profile_has_list_of_its_translations_only(
        client, user, user2, published_translation):
    login(client, user.email, 'password')
    assert published_translation.authors == [user]
    published_translation.modify(translators=[user2])
    response = client.get(f'/en/profile/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert published_translation.detail_url not in response
    response = client.get(f'/en/profile/{user2.id}/')
    assert response.status_code == HTTPStatus.OK
    assert published_translation.detail_url in response


def test_editor_can_promote_user_as_editor(client, user, editor):
    login(client, editor.email, 'password')
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert not user.has_role('editor')
    assert 'name=editor' in response
    client.post(f'/en/profile/{user.id}/edit/', data={'editor': '1'})
    user.reload()
    assert user.has_role('editor')


def test_editor_can_remove_editor_role(client, user, editor):
    login(client, editor.email, 'password')
    current_app.user_datastore.add_role_to_user(user, 'editor')
    client.post(f'/en/profile/{user.id}/edit/', data={'editor': ''})
    user.reload()
    assert not user.has_role('editor')


def test_user_cannot_promote_as_editor(client, user):
    login(client, user.email, 'password')
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert not user.has_role('editor')
    assert 'name=editor' not in response
    client.post(f'/en/profile/{user.id}/edit/', data={'editor': '1'})
    user.reload()
    assert not user.has_role('editor')
