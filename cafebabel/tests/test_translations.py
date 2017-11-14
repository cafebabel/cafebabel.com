from http import HTTPStatus

from flask.helpers import get_flashed_messages

from ..articles.models import Article
from ..translations.models import Translation
from .utils import login


def test_translation_query_should_retrieve_all(app, article, translation):
    french = app.config['LANGUAGES'][1][0]
    article2 = Article.objects.create(
        title='title',
        summary='summary text',
        language=french,
        body='body text')
    assert Article.objects.filter(language=french).count() == 2
    articles = Article.objects.filter(language=french).only('id')
    assert article2.id in [a.id for a in articles]
    assert translation.id in [a.id for a in articles]
    assert article.id not in [a.id for a in articles]


def test_translation_creation_should_display_form(app, client, user, article):
    login(client, user.email, 'secret')
    language = app.config['LANGUAGES'][1][0]
    response = client.get(f'/translation/?lang={language}&from={article.id}')
    assert response.status_code == HTTPStatus.OK
    text = response.get_data(as_text=True)
    assert '<textarea id=body name=body required></textarea>' in text


def test_translation_creation_requires_login(app, client, article):
    language = app.config['LANGUAGES'][1][0]
    response = client.get(f'/translation/?lang={language}&from={article.id}')
    assert response.status_code == HTTPStatus.FOUND
    assert '/login?next=%2Ftranslation%2F' in response.headers.get('Location')


def test_translation_creation_required_parameters(app, client, user, article):
    login(client, user.email, 'secret')
    language = app.config['LANGUAGES'][1][0]
    response = client.get(f'/translation/?from={article.id}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    response = client.get(f'/translation/?lang={language}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    response = client.get(f'/translation/?lang={language}&from={article.id}$')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_creation_should_redirect(app, client, user, article):
    login(client, user.email, 'secret')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'title',
        'summary': 'summary',
        'body': 'body',
    }
    response = client.post(
        f'/translation/?lang={language}&from={article.id}', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            f'http://localhost/translation/{translation.id}/')
    assert (get_flashed_messages() ==
            ['Your translation was successfully created.'])


def test_translation_creation_already_existing(app, client, user, article):
    login(client, user.email, 'secret')
    language = app.config['LANGUAGES'][1][0]
    translation = Translation(
        title='foo', summary='summary', body='bar', translated_from=article.id,
        translator=user.id, language=language, status='published')
    translation.save()
    data = {
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
    }
    response = client.post(
        f'/translation/?lang={language}&from={article.id}', data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert ('Existing translation already exists.'
            in response.get_data(as_text=True))


def test_translation_creation_same_as_article(app, client, user, article):
    login(client, user.email, 'secret')
    data = {
        'title': 'Test article',
        'body': 'Article body',
    }
    response = client.post(
        f'/translation/?lang={article.language}&from={article.id}', data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert ('Original article in the same language.'
            in response.get_data(as_text=True))


def test_translation_creation_unknown_article(app, client, user, article):
    login(client, user.email, 'secret')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'Test article',
        'body': 'Article body',
    }
    response = client.post(
        f'/translation/?lang={language}&from=foo{article.id}', data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_access_draft_should_return_200(client, translation):
    response = client.get(f'/translation/{translation.id}/')
    assert response.status_code == HTTPStatus.OK


def test_translation_access_have_translated_from_link(client, translation):
    response = client.get(f'/translation/{translation.id}/')
    text = response.get_data(as_text=True)
    assert ((f'Translated from '
             f'<a href="/draft/{translation.translated_from.id}/">title')
            in text)


def test_translation_access_have_translator(client, translation):
    response = client.get(f'/translation/{translation.id}/')
    text = response.get_data(as_text=True)
    assert f'by {translation.translator}.' in text


def test_translation_access_published_should_return_404(client, translation):
    translation.status = 'published'
    translation.save()
    response = client.get(f'/translation/{translation.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_access_wrong_id_should_return_404(client, translation):
    response = client.get(f'/translation/foo{translation.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_update_should_display_form(client, user, translation):
    login(client, user.email, 'secret')
    response = client.get(f'/translation/{translation.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    text = response.get_data(as_text=True)
    assert '<textarea id=body name=body required>body text</textarea>' in text


def test_translation_update_requires_login(client, translation):
    response = client.get(f'/translation/{translation.id}/edit/')
    assert response.status_code == HTTPStatus.FOUND
    assert '/login?next=%2Ftranslation%2F' in response.headers.get('Location')


def test_translation_update_values_should_redirect(client, user, translation):
    login(client, user.email, 'secret')
    data = {
        'title': 'Modified title',
        'summary': 'Modified summary',
        'body': 'Modified body',
    }
    response = client.post(f'/translation/{translation.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            f'http://localhost/translation/{translation.id}/')
    assert translation.title == 'Modified title'
    assert (get_flashed_messages() ==
            ['Your translation was successfully updated.'])


def test_translation_update_empty_summary(client, user, translation):
    login(client, user.email, 'secret')
    data = {
        'title': translation.title,
        'summary': '',
        'body': translation.body,
    }
    response = client.post(f'/translation/{translation.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            f'http://localhost/translation/{translation.id}/')
    assert translation.summary == ''
    assert (get_flashed_messages() ==
            ['Your translation was successfully updated.'])


def test_translation_published_should_return_200(client, translation):
    translation.status = 'published'
    translation.save()
    response = client.get(f'/article/{translation.slug}-{translation.id}/')
    assert response.status_code == HTTPStatus.OK


def test_translation_published_should_have_translator(client, translation):
    translation.status = 'published'
    translation.save()
    response = client.get(f'/article/{translation.slug}-{translation.id}/')
    text = response.get_data(as_text=True)
    assert response.status_code == HTTPStatus.OK
    assert ((f'Translated from '
             f'<a href="/draft/{translation.translated_from.id}/">title')
            in text)
    assert f'by {translation.translator}.' in text


def test_translation_published_should_have_reference(client, translation):
    translation.status = 'published'
    translation.save()
    article = translation.translated_from
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    text = response.get_data(as_text=True)
    assert response.status_code == HTTPStatus.OK
    assert '<p>Read this article in:</p>' in text
    assert ((f'<li>{translation.language}: <a href={translation.detail_url}>'
             f'{translation.title}</a></li>') in text)