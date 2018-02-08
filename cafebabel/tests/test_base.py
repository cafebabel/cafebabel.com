from http import HTTPStatus


def test_homepage_is_redirecting_to_default_language(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get('location') == 'http://localhost/en/'


def test_homepage_is_displaying(client):
    response = client.get('/en/')
    assert ('<meta name=description content="Cafébabel is the first European '
            'participatory magazine made for young Europeans across borders.">'
            in response)
    assert '<meta property=og:url content="http://localhost/en/">' in response
    assert '<meta name=twitter:card content="summary">' in response
