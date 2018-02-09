from http import HTTPStatus

from flask import url_for

from cafebabel.articles.models import ArticleArchive


def test_archive_is_redirect_to_article_with_lang(client, published_article):
    url = 'http://cafebabel.test/lifestyle/article/ancien-article.html'
    published_article.modify(language='fr',
                             archive=ArticleArchive(id=1, url=url))
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response.location == ('http://cafebabel.test/fr/article/'
                                 f'{published_article.slug}-'
                                 f'{published_article.id}/')


def test_archive_is_redirect_from_production(app, client, published_article):
    url_prod = 'http://www.cafebabel.co.uk/lifestyle/article/old-article.html'
    url_preprod = ('http://preprod.cafebabel.co.uk/lifestyle/article/'
                   'old-article.html')
    published_article.modify(archive=ArticleArchive(id=1, url=url_prod))
    old_server_name = app.config['SERVER_NAME']
    old_domain_name = app.config['DOMAIN_NAME']
    app.config['SERVER_NAME'] = 'preprod.cafebabel.co.uk'
    app.config['DOMAIN_NAME'] = 'cafebabel.redirect'
    response = client.get(url_preprod)
    app.config['SERVER_NAME'] = old_server_name
    app.config['DOMAIN_NAME'] = old_domain_name
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response.location == (
        f'http://cafebabel.redirect/en/article/{published_article.slug}-'
        f'{published_article.id}/'
    )


def test_archive_is_redirect_to_translation(client, translation):
    url = 'http://cafebabel.test/lifestyle/articolo/old-translation.html'
    translation.modify(archive=ArticleArchive(id=1, url=url),
                       status='published')
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    article_url = (f'http://cafebabel.test/fr/article/{translation.slug}-'
                   f'{translation.id}/')
    assert response.location == article_url


def test_archive_inexisting_renders_404(client, published_article):
    url = 'http://cafebabel.test/lifestyle/article/non-existing-archive.html'
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
