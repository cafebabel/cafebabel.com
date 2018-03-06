from http import HTTPStatus

from cafebabel.articles.tags.models import Tag
from flask import url_for


def test_homepage_is_redirecting_to_default_language(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get('location') == 'http://localhost/en/'


def test_homepage_is_displaying(client):
    response = client.get('/en/')
    assert ('<meta name=description content="Cafébabel is the first European '
            'participatory magazine made for young Europeans across borders.">'
            in response)
    assert ('<meta property=og:url content="http://localhost/en/">'
            in response)
    assert '<meta name=twitter:card content="summary">' in response


def test_homepage_contains_published_articles(client, published_article):
    response = client.get('/en/')
    assert published_article.title in response
    assert (url_for(
        'articles.detail',
        slug=published_article.slug, article_id=published_article.pk)
        in response)


def test_homepage_does_not_contain_draft_articles(client, article):
    response = client.get('/en/')
    assert article.title not in response
    assert (url_for(
        'articles.detail', slug=article.slug, article_id=article.pk)
        not in response)


def test_homepage_contains_categories(app, client, published_article):
    language = app.config['LANGUAGES'][0][0]
    assert 'impact' in app.config['CATEGORIES']
    impact = Tag.objects.create(name='Impact', language=language)
    response = client.get('/en/')
    assert impact.name in response
    assert url_for('tags.detail', slug=impact.slug) in response


def test_homepage_contains_authors_links(client, published_article):
    response = client.get('/en/')
    assert (f'<a href=/en/profile/{published_article.author.pk}/>'
            f'{published_article.author.profile.name}</a>' in response)


def test_logo_from_home_is_redirecting_to_localized_homepage(client):
    response = client.get('/fr/')
    assert '<a href=/fr/ class=logo>' in response


def test_logo_from_tag_is_redirecting_to_localized_homepage(client, tag):
    response = client.get('/en/article/tag/wonderful/')
    assert '<a href=/en/ class=logo>' in response
