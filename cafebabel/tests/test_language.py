from http import HTTPStatus


def test_homepage_is_redirecting_to_browser_language(client):
    response = client.get('/', headers={
        'Accept-Language': 'fr-FR,fr;q=0.5',
    })
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get('location') == 'http://localhost/fr/'


def test_homepage_is_redirecting_unknown_language_to_default(client):
    response = client.get('/', headers={
        'Accept-Language': 'xx-XX,xx;q=0.5',
    })
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get('location') == 'http://localhost/en/'


def test_homepage_displays_languages_meta(client):
    response = client.get('/fr/')
    assert 'og:locale content="fr"' in response
    assert 'og:url content="http://localhost/fr/"' in response
    assert 'twitter:url content="http://localhost/fr/"' in response


def test_wrong_language_raises_404(client):
    response = client.get('/profile/')
    assert response.status_code == HTTPStatus.NOT_FOUND
