def login(client, email, password):
    response = client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)
    assert b'action="/login"' not in response.data, response.data
    return response


def logout(client):
    return client.get('/logout', follow_redirects=True)
