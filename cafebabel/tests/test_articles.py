
def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/article/proposal/')
    assert response.status_code == 200
    assert 'action=/article/proposal/' in response.get_data().decode()
