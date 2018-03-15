from flask.helpers import get_flashed_messages

from .. import mail


def test_proposal_display_form(app, client):
    response = client.get('/en/article/proposal/new/')
    assert response.status_code == 200
    assert '<form action=. method=post>' in response


def test_proposal_display_emails(app, client):
    response = client.get('/en/article/proposal/new/')
    assert response.status_code == 200
    assert ('m&#x61;ilto:editors@c&amp;#x61;feb&amp;#x61;bel&amp;#46;com'
            in response)


def test_proposal_send_email(app, client):
    mail.init_app(app)  # Re-load using test configuration.
    with mail.record_messages() as outbox:
        response = client.post('/de/article/proposal/new/', data={
            'email': 'email@example.com',
            'topic': 'Topic',
            'name': 'Name',
            'media': 'video',
            'section': 'creative',
            'city': 'City',
            'angle': 'Angle',
            'format': 'Format',
            'additional': 'Additional'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0].subject == 'Article proposal: Topic'
        assert outbox[0].body == f'''
Language: de
Name: Name
Email: email@example.com
City: City
Topic: Topic
Angle: Angle
Media: video
Format: Format
Section: creative
Addiction comment: Additional
'''
    assert (get_flashed_messages() ==
            ['Thanks! We’ll be getting back to you asap'])
