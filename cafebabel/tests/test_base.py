
def test_homepage_is_displaying(client):
    response = client.get('/')
    assert response.status_code == 200
    assert ('<meta name=description content="pan-European news, features and '
            'opinions">' in response)
    assert '<meta property=og:url content="http://localhost/">' in response
    assert '<meta name=twitter:card content="summary">' in response
