from http import HTTPStatus

from flask import url_for

from cafebabel.articles.models import ArticleArchive


def test_archive_is_redirect_to_artile(client, published_article):
    url = 'http://localhost/lifestyle/article/old-artile.html'
    published_article.archive = ArticleArchive(id=1, url=url)
    published_article.save()
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    article_url = url_for('articles.detail', slug=published_article.slug,
                          article_id=published_article.id, _external=True)
    assert response.location == article_url


def test_archive_is_redirect_to_translation(client, translation):
    url = 'http://localhost/lifestyle/articolo/old-translation.html'
    translation.status = 'published'
    translation.archive = ArticleArchive(id=1, url=url)
    translation.save()
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    article_url = url_for('articles.detail', slug=translation.slug,
                          article_id=translation.id, _external=True)
    assert response.location == article_url


def test_archive_inexisting_renders_404(client, published_article):
    url = 'http://localhost/lifestyle/article/non-existing-archive.html'
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
