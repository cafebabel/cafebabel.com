
def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/articles/proposal/')
    assert response.status_code == 200
    assert 'action=/article/proposal/' in response.body
