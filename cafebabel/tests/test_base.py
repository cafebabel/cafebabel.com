from http import HTTPStatus

from cafebabel.articles.tags.models import Tag
from flask import abort, url_for


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


def test_homepage_contains_static_pages_if_present(client, published_article):
    response = client.get('/en/')
    assert '<a href=#>About</a>' in response
    published_article.modify(slug='about')
    response = client.get('/en/')
    assert (f'<a href=/en/article/about-{published_article.id}/>About</a>'
            in response)


def test_homepage_contains_authors_links(client, published_article):
    response = client.get('/en/')
    assert (f'<a href=/en/profile/{published_article.authors[0].pk}/>'
            f'{published_article.authors[0].profile.name}</a>' in response)


def test_logo_from_home_is_redirecting_to_localized_homepage(client):
    response = client.get('/fr/')
    assert '<a href=/fr/ class=logo>' in response


def test_logo_from_tag_is_redirecting_to_localized_homepage(client, tag):
    response = client.get('/en/article/tag/wonderful/')
    assert '<a href=/en/ class=logo>' in response


def test_error_not_found(client):
    response = client.get('/foobar/')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert '404 error' in response


def test_error_internal_server_error(app, client):

    @app.route('/foobar/')
    def error():
        abort(500)

    response = client.get('/foobar/')
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert '500 error' in response
