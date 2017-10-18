
def test_homepage_is_displaying(client):
    response = client.get('/')
    assert response.status_code == 200
