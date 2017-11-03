from http import HTTPStatus

from ..articles.models import Article
from .utils import login


def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/article/proposal/')
    assert response.status_code == 200
    assert 'action=/article/proposal/' in response.get_data().decode()


def test_delete_article_should_return_200(client, user, article):
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    response.status_code == HTTPStatus.OK
    assert Article.objects.all().count() == 0


def test_delete_incorrect_id_should_return_404(client, user, article):
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/',
                           follow_redirects=True)
    response.status_code == HTTPStatus.NOT_FOUND
    assert Article.objects.all().count() == 1


def test_delete_inexistent_article_should_return_404(client, user, article):
    article.delete()
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    response.status_code == HTTPStatus.NOT_FOUND
