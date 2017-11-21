from http import HTTPStatus
from pathlib import Path
from io import BytesIO

from flask import request

from ..articles.models import Article
from .utils import login
from .. import app


def test_create_draft_should_display_form(client, editor):
    login(client, editor.email, 'secret')
    response = client.get('/article/draft/new/')
    assert response.status_code == 200
    assert '<input id=title' in response.get_data(as_text=True)


def test_create_draft_should_generate_article(client, editor):
    login(client, editor.email, 'secret')
    response = client.post('/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
    }, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert '<h1>Test article</h1>' in body
    assert '<p>Article body</p>' in body


def test_create_published_draft_should_display_article(client, editor):
    login(client, editor.email, 'secret')
    response = client.post('/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'status': 'published',
    }, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert request.url_rule.endpoint == 'articles.detail'
    assert '<h1>Test article</h1>' in body
    assert '<p>Article body</p>' in body


def test_draft_editing_should_update_content(client, editor):
    login(client, editor.email, 'secret')
    data = {
        'title': 'My article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
    }
    draft = Article.objects.create(**data)
    updated_data = data.copy()
    updated_data['language'] = 'fr'
    response = client.post(f'/article/draft/{draft.id}/edit/',
                           data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    updated_draft = Article.objects.get(id=draft.id)
    assert updated_draft.id == draft.id
    assert updated_draft.language == 'fr'
    assert updated_draft.title == 'My article'


def test_draft_image_should_save_and_render(client, editor):
    login(client, editor.email, 'secret')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image = BytesIO(content.read())
    data = {
        'title': 'My article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'image': (image, 'image-name.jpg'),
    }
    response = client.post('/article/draft/new/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    article = Article.objects.first()
    assert article.has_image
    assert Path(app.config.get('ARTICLES_IMAGES_PATH') /
                str(article.id)).exists()
    assert f'<img src="{article.image_url}"' in response.get_data(as_text=True)


def test_draft_should_not_offer_social_sharing(client, article):
    response = client.get(f'/article/draft/{article.id}/')
    assert response.status_code == 200
    assert 'facebook.com/sharer' not in response.get_data(as_text=True)


def test_visitor_cannot_change_editor_nor_author(client, editor, user,
                                                 article):
    article.modify(status='draft', author=user, editor=editor)
    client.post(f'/article/draft/{article.id}/edit/', data={
        'title': 'Updated draft',
        'author': editor,
    })
    article.reload()
    assert article.title == 'Updated draft'
    assert article.author == user
    assert article.editor == editor


def test_access_published_draft_should_return_404(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/draft/{article.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND
