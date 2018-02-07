def login(client, email, password):
    response = client.post('/en/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)
    assert b'action="/en/login"' not in response.data, response.data
    return response


def logout(client):
    return client.get('/en/logout', follow_redirects=True)
