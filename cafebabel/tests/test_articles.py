from http import HTTPStatus

from flask.helpers import get_flashed_messages

from ..articles.models import Article
from .utils import login


def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/article/proposal/')
    assert response.status_code == 200
    assert 'action=/article/proposal/' in response.get_data().decode()


def test_delete_article_should_return_200(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert Article.objects.all().count() == 0
    assert get_flashed_messages() == ['Article was deleted.']


def test_delete_regular_user_should_return_403(client, user, article):
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Article.objects.all().count() == 1


def test_delete_incorrect_id_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Article.objects.all().count() == 1


def test_delete_inexistent_article_should_return_404(client, editor, article):
    article.delete()
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.NOT_FOUND
