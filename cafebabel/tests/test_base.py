from http import HTTPStatus

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


def test_homepage_contains_published_articles(client, published_article):
    response = client.get('/en/')
    assert published_article.title in response
    assert published_article.detail_url in response


def test_homepage_does_not_contain_draft_articles(client, article):
    response = client.get('/en/')
    assert article.title not in response
    assert article.detail_url not in response


def test_homepage_contains_categories(app, client, published_article):
    language = app.config['LANGUAGES'][0][0]
    assert 'impact' in app.config['CATEGORIES']
    impact = Tag.objects.create(name='Impact', language=language)
    response = client.get('/en/')
    assert impact.name in response
    assert impact.detail_url in response


def test_homepage_contains_authors_links(app, client, published_article):
    response = client.get('/en/')
    assert (f'<a href=/en/profile/{published_article.author.pk}/>'
            f'{published_article.author.profile.name}</a>' in response)
