from http import HTTPStatus

from flask.helpers import get_flashed_messages

from ..articles.models import Article
from .utils import login


def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/article/proposal/')
    assert response.status_code == 200
    assert 'action=/article/proposal/' in response.get_data().decode()


def test_create_draft_should_render_article(client, editor):
    login(client, editor.email, 'secret')
    response = client.post('/article/draft/', data={
        'title': 'My article',
        'language': 'en',
        'body': 'Article body',
    }, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert '<h1>My article</h1>' in body
    assert '<p>Article body</p>' in body


def test_draft_editing_should_update_content(client, editor):
    login(client, editor.email, 'secret')
    data = {'title': 'My article', 'language': 'en', 'body': 'Article body'}
    draft = Article.objects.create(**data)
    updated_data = data.copy()
    updated_data['language'] = 'fr'
    response = client.post(f'/article/draft/{draft.uid}/edit/',
                           data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    updated_draft = Article.objects.get(uid=draft.uid)
    assert updated_draft.id == draft.id
    assert updated_draft.language == 'fr'
    assert updated_draft.title == 'My article'


def test_draft_image_should_save_and_render(client, editor):
    login(client, editor.email, 'secret')
    data = {'title': 'My article', 'language': 'en', 'body': 'Article body'}
    response = client.post('/article/draft/', data=data, follow_redirects=True)


def test_access_published_article_should_return_200(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_article_with_large_slug_should_return_200(client, article):
    article.status = 'published'
    article.slug = 'quite-large-slug-with-dashes'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_draft_article_should_return_404(client, article):
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_article_should_return_404(client):
    response = client.get(f'/article/foo-bar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_id_should_return_404(client):
    response = client.get(f'/article/foobar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_old_slug_article_should_return_301(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/wrong-slug-{article.id}/')
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY


def test_delete_article_should_return_200(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert Article.objects.all().count() == 0
    assert get_flashed_messages() == ['Article was deleted.']


def test_delete_article_regular_user_should_return_403(client, user, article):
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Article.objects.all().count() == 1


def test_delete_incorrect_id_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Article.objects.all().count() == 1


def test_delete_inexistent_article_should_return_404(client, editor, article):
    article.delete()
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.NOT_FOUND
