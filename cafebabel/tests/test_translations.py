from http import HTTPStatus

import pytest
import mongoengine
from flask.helpers import get_flashed_messages

from ..articles.models import Article
from ..articles.translations.models import Translation
from .utils import login


def test_translation_query_should_retrieve_all(app, article, translation):
    language = app.config['LANGUAGES'][1][0]
    article2 = Article.objects.create(
        title='title',
        summary='summary text',
        language=language,
        body='body text')
    assert Article.objects.filter(language=language).count() == 2
    articles = Article.objects.filter(language=language).only('id')
    assert article2.id in [a.id for a in articles]
    assert translation.id in [a.id for a in articles]
    assert article.id not in [a.id for a in articles]


def test_translation_creation_should_display_form(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    response = client.get(
        f'/en/article/translation/new/?lang={language}&original={article.id}')
    assert response.status_code == HTTPStatus.OK
    assert '<textarea id=body name=body required></textarea>' in response


def test_translation_creation_should_limit_languages(app, client, user,
                                                     translation):
    login(client, user.email, 'password')
    response = client.get(
        f'/en/article/draft/{translation.original_article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert ('href="/en/article/translation/new/?lang='
            f'{app.config["LANGUAGES"][2][0]}' in response)
    assert (f'href="/en/article/translation/new/?lang={translation.language}'
            not in response)
    assert f'value={translation.original_article.language}' not in response


def test_translation_creation_requires_login(app, client, article):
    language = app.config['LANGUAGES'][1][0]
    response = client.get(
        f'/en/article/translation/new/?lang={language}&original={article.id}')
    assert response.status_code == HTTPStatus.FOUND
    assert ('/en/login?next=%2Fen%2Farticle%2Ftranslation%2F'
            in response.headers.get('Location'))


def test_translation_creation_required_parameters(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    response = client.get(
        f'/en/article/translation/new/?original={article.id}')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response = client.get(f'/en/article/translation/new/?lang={language}')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response = client.get(
        f'/en/article/translation/new/?lang={language}&original={article.id}$')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_creation_should_redirect(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'title',
        'summary': 'summary',
        'body': 'body',
        'original': article.id,
        'language': language
    }
    response = client.post(f'/en/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            f'http://localhost/en/article/translation/{translation.id}/')
    assert (get_flashed_messages() ==
            ['Your translation was successfully created.'])


def test_translation_creation_should_keep_image(app, client, user, article):
    login(client, user.email, 'password')
    article.modify(image_filename='/articles/image-name.jpg')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'title',
        'summary': 'summary',
        'body': 'body',
        'original': article.id,
        'language': language
    }
    response = client.post('/en/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert translation.image_filename == '/articles/image-name.jpg'
    assert translation.image_url == '/articles/image-name.jpg'
    assert str(translation.image_path).endswith(
        '/cafebabel/uploads/articles/image-name.jpg')


def test_translation_creation_already_existing(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    translation = Translation(
        title='foo', summary='summary', body='bar',
        original_article=article.id, translators=[user.id], language=language,
        status='published')
    translation.save()
    data = {
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'original': article.id,
        'language': language
    }
    response = client.post('/en/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'This article already exists in this language.' in response


def test_translation_creation_same_as_article(app, client, user, article):
    login(client, user.email, 'password')
    data = {
        'title': 'Test article',
        'body': 'Article body',
        'original': article.id,
        'language': article.language
    }
    response = client.post('/en/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'This article already exists in this language.' in response


def test_translation_creation_unknown_article(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'Test article',
        'body': 'Article body',
        'original': f'foo{article.id}',
        'language': language
    }
    response = client.post(f'/en/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_access_draft_should_return_200(client, translation):
    response = client.get(f'/en/article/translation/{translation.id}/')
    assert response.status_code == HTTPStatus.OK


def test_translation_access_have_original_article_link(client, translation):
    response = client.get(f'/en/article/translation/{translation.id}/')
    assert ((f'Translated from '
             f'<a href="/en/article/draft/{translation.original_article.id}/">'
             f'article title') in response)


def test_translation_can_have_raw_summary(client, translation):
    response = client.get(f'/en/article/translation/{translation.id}/')
    assert '<div class=summary><p>summary text</p></div>' in response
    assert '<meta name=description content="summary text">' in response


def test_translation_can_have_html_summary(client, translation):
    translation.modify(summary='<p>summary text</p>')
    response = client.get(f'/en/article/translation/{translation.id}/')
    assert '<div class=summary><p>summary text</p></div>' in response
    assert '<meta name=description content="summary text">' in response


def test_translation_access_have_translator(client, translation):
    response = client.get(f'/en/article/translation/{translation.id}/')
    assert f'by {translation.translators[0]}.' in response


def test_translation_access_published_should_return_404(client, translation):
    translation.status = 'published'
    translation.save()
    response = client.get(f'/en/article/translation/{translation.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_access_wrong_id_should_return_404(client, translation):
    response = client.get(f'/en/article/translation/foo{translation.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_update_should_display_form(client, user, translation):
    login(client, user.email, 'password')
    response = client.get(f'/en/article/translation/{translation.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert ('<textarea id=body name=body required>body text</textarea>'
            in response)


def test_translation_update_requires_login(client, translation):
    response = client.get(f'/en/article/translation/{translation.id}/edit/')
    assert response.status_code == HTTPStatus.FOUND
    assert ('/en/login?next=%2Fen%2Farticle%2Ftranslation%2F'
            in response.headers.get('Location'))


def test_translation_update_values_should_redirect(client, user, translation):
    login(client, user.email, 'password')
    data = {
        'title': 'Modified title',
        'summary': 'Modified summary',
        'body': 'Modified body',
    }
    response = client.post(
        f'/en/article/translation/{translation.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            f'http://localhost/en/article/translation/{translation.id}/')
    assert translation.title == 'Modified title'
    assert (get_flashed_messages() ==
            ['Your translation was successfully updated.'])


def test_translation_published_should_return_200(client, translation):
    translation.modify(status='published')
    response = client.get(f'/en/article/{translation.slug}-{translation.id}/')
    assert response.status_code == HTTPStatus.OK


def test_translation_published_should_have_translator(client, translation):
    translation.status = 'published'
    translation.save()
    response = client.get(f'/en/article/{translation.slug}-{translation.id}/')
    assert response.status_code == HTTPStatus.OK
    assert ((f'Translated from '
             f'<a href="/en/article/draft/{translation.original_article.id}/">'
             f'article title') in response)
    assert f'by {translation.translators[0]}.' in response


def test_translation_published_should_have_reference(client, translation):
    translation.modify(status='published')
    article = translation.original_article
    article.modify(status='published')
    response = client.get(f'/en/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert ((f'<li class=translated-language><a href='
             f'/en/article/title-{translation.id}/>') in response)


def test_article_model_is_translated_in(translation):
    article = translation.original_article
    assert article.is_translated_in(translation.language)
    assert not article.is_translated_in('dummy')


def test_article_model_get_translation(translation):
    article = translation.original_article
    assert article.get_translation(translation.language) == translation
    assert article.get_translation('dummy') is None


def test_translation_editing_language_prevents_duplicates(translation):
    translation.language = translation.original_article.language
    with pytest.raises(mongoengine.errors.NotUniqueError) as error:
        translation.save()
    assert str(error.value) == 'This article already exists in this language.'
