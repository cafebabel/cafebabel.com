from http import HTTPStatus
from io import BytesIO
from pathlib import Path

from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag
from flask.helpers import get_flashed_messages

from .utils import login


def test_tag_basics(tag):
    assert tag.slug == 'wonderful'
    assert str(tag) == 'Wonderful (en)'


def test_tag_deleted_remove_article_reference(app, tag, article):
    language = app.config['LANGUAGES'][0][0]
    tag2 = Tag.objects.create(name='Sensational', language=language)
    article.modify(tags=[tag, tag2])
    assert Article.objects(tags__in=[tag]).count() == 1
    assert Article.objects(tags__all=[tag, tag2]).count() == 1
    tag2.delete()
    article.reload()
    assert article.tags == [tag]


def test_tag_suggest_basics(client, tag):
    response = client.get('/article/tag/suggest/?language=en&terms=wond')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'language': 'en',
        'name': 'Wonderful',
        'slug': 'wonderful',
        'summary': 'summary text'
    }]


def test_tag_suggest_many(client, app, tag):
    language = app.config['LANGUAGES'][0][0]
    Tag.objects.create(name='Wondering', language=language)
    response = client.get('/article/tag/suggest/?language=en&terms=wond')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'language': 'en',
        'name': 'Wonderful',
        'slug': 'wonderful',
        'summary': 'summary text'
    }, {
        'language': 'en',
        'name': 'Wondering',
        'slug': 'wondering',
        'summary': ''
    }]


def test_tag_only_language(client, app, tag):
    language = app.config['LANGUAGES'][1][0]
    Tag.objects.create(name='Wondering', language=language)
    response = client.get('/article/tag/suggest/?language=fr&terms=wond')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'language': 'fr',
        'name': 'Wondering',
        'slug': 'wondering',
        'summary': ''
    }]


def test_tag_suggest_too_short(client, tag):
    response = client.get('/article/tag/suggest/?language=en&terms=wo')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert (b'Suggestions made available from 3-chars and more.'
            in response.data)


def test_tag_suggest_wrong_language(client, tag):
    response = client.get('/article/tag/suggest/?language=ca&terms=wond')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Languages available: ['en', 'fr', 'es', 'it', 'de']" in response


def test_tag_detail(client, tag, published_article):
    published_article.modify(tags=[tag])
    response = client.get('/article/tag/wonderful/')
    assert response.status_code == HTTPStatus.OK
    assert tag.name in response
    assert published_article.title in response


def test_tag_detail_draft(client, tag, article):
    article.modify(tags=[tag])
    response = client.get('/article/tag/wonderful/')
    assert response.status_code == HTTPStatus.OK
    assert tag.name in response
    assert article.title not in response


def test_tag_detail_unknown(client, tag):
    response = client.get('/article/tag/sensational/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_tag_update_basics(app, client, tag, editor):
    Tag.objects.create(name='Wonderful',
                       language=app.config['LANGUAGES'][1][0])
    login(client, editor.email, 'password')
    language = app.config['LANGUAGES'][2][0]
    data = {
        'name': 'updated name',
        'language': language,
        'summary': 'custom summary'
    }
    response = client.post(f'/article/tag/{tag.slug}/edit/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your tag was successfully saved.']
    tag.reload()
    assert tag.name == 'updated name'
    assert tag.language == language
    assert tag.summary == 'custom summary'
    assert 'updated name' in response


def test_tag_update_image(app, client, tag, editor):
    login(client, editor.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image_content = BytesIO(content.read())
    data = {
        'name': 'updated name',
        'language': language,
        'summary': 'custom summary',
        'image': (image_content, 'image-name.jpg'),
    }
    response = client.post(f'/article/tag/{tag.slug}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your tag was successfully saved.']
    tag.reload()
    assert tag.name == 'updated name'
    assert tag.language == language
    assert tag.summary == 'custom summary'
    assert 'updated name' in response
    assert tag.has_image
    assert Path(app.config.get('TAGS_IMAGES_PATH') / str(tag.id)).exists()
