from http import HTTPStatus

from cafebabel.articles.models import ArticleArchive


def test_archive_is_redirect_to_article_with_lang(client, published_article):
    url = 'http://localhost/lifestyle/article/ancien-article.html'
    published_article.modify(language='fr',
                             archive=ArticleArchive(id=1, url=url))
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response.location == ('http://localhost/fr/article/'
                                 f'{published_article.slug}-'
                                 f'{published_article.id}/')

def test_archive_is_redirect_to_article_with_lang_in_url(client,
                                                         published_article):
    url = 'http://localhost/fr/lifestyle/article/ancien-article.html'
    published_article.modify(language='fr',
                             archive=ArticleArchive(id=1, url=url))
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response.location == ('http://localhost/fr/article/'
                                 f'{published_article.slug}-'
                                 f'{published_article.id}/')


def test_archive_is_redirect_from_production(app, client, published_article):
    url_prod = 'http://www.cafebabel.co.uk/lifestyle/article/old-article.html'
    url_preprod = ('http://preprod.cafebabel.co.uk/lifestyle/article/'
                   'old-article.html')
    published_article.modify(archive=ArticleArchive(id=1, url=url_prod))
    response = client.get(url_preprod, headers={'Archive': url_prod})
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    assert response.location == (
        f'http://preprod.cafebabel.co.uk/en/article/{published_article.slug}-'
        f'{published_article.id}/'
    )


def test_archive_is_redirect_to_translation(client, translation):
    url = 'http://localhost/lifestyle/articolo/old-translation.html'
    translation.modify(archive=ArticleArchive(id=1, url=url),
                       status='published')
    response = client.get(url)
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
    article_url = (f'http://localhost/fr/article/{translation.slug}-'
                   f'{translation.id}/')
    assert response.location == article_url


def test_archive_inexisting_renders_404(client, published_article):
    url = 'http://localhost/lifestyle/article/non-existing-archive.html'
    response = client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
