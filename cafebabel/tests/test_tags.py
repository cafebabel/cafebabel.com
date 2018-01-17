from http import HTTPStatus

from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag


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
