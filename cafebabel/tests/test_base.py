from http import HTTPStatus

from flask import abort

from cafebabel.articles.tags.models import Tag


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


def test_homepage_does_not_contain_draft_articles(client, article):
    response = client.get('/en/')
    assert article.title not in response
    assert article.detail_url not in response


def test_homepage_contains_categories(app, client, published_article):
    language = app.config['LANGUAGES'][0][0]
    assert 'impact' in app.config['CATEGORIES_SLUGS']
    impact = Tag.objects.create(name='Impact', language=language)
    response = client.get('/en/')
    assert impact.name in response
    assert impact.detail_url in response


def test_homepage_contains_tag_editors_pick(app, client, published_article):
    language = app.config['LANGUAGES'][0][0]
    editors_pick = Tag.objects.create(name='Editors pick', language=language)
    published_article.modify(tags=[editors_pick])
    response = client.get('/en/')
    assert editors_pick.name in response
    assert response.contains_only_once(
        f'<a href={published_article.detail_url}>{published_article.title}</a>'
    )


def test_homepage_contains_static_pages_if_present(client, published_article):
    response = client.get('/en/')
    assert '<a href=#>About us</a>' in response
    published_article.modify(slug='about-us')
    response = client.get('/en/')
    assert (
        f'<a href=/en/article/about-us-{published_article.id}/>About us</a>'
        in response
    )


def test_homepage_contains_authors_links(client, published_article):
    response = client.get('/en/')
    assert (f'<a href=/en/profile/{published_article.authors[0].id}/>'
            f'{published_article.authors[0].profile.name}</a>' in response)


def test_logo_from_home_is_redirecting_to_localized_homepage(client):
    response = client.get('/fr/')
    assert '<a href=/fr/ class=logo>' in response


def test_logo_from_tag_is_redirecting_to_localized_homepage(client, tag):
    response = client.get('/en/article/tag/wonderful/')
    assert '<a href=/en/ class=logo>' in response


def test_social_networks_are_redirected_to_localized_accounts(client):
    response = client.get('/en/')
    assert '<a href=https://www.facebook.com/cafebabelmagazine/' in response
    response = client.get('/fr/')
    assert '<a href=https://www.facebook.com/cafebabelfrance/' in response


def test_social_networks_fallback_on_english_accounts(client):
    response = client.get('/en/')
    assert '<a href=https://www.instagram.com/inside.cafebabel/' in response
    response = client.get('/fr/')
    assert '<a href=https://www.instagram.com/inside.cafebabel/' in response


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
