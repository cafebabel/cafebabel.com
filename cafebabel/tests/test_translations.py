from http import HTTPStatus

import pytest
import mongoengine
from flask.helpers import get_flashed_messages

from .. import mail
from ..articles.models import Article
from ..articles.tags.models import Tag
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


def test_translation_creation_should_display_form(client, user, article):
    login(client, user.email, 'password')
    response = client.get(
        f'/fr/article/translation/new/?original={article.id}')
    assert response.status_code == HTTPStatus.OK
    assert f'value="{article.title}"'in response
    assert f'>{article.summary}</textarea>' in response
    assert f'required>{article.body}</textarea>' in response


def test_translation_creation_should_limit_languages(client, user,
                                                     translation):
    login(client, user.email, 'password')
    response = client.get(
        f'/en/article/draft/{translation.original_article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert 'href="/de/article/translation/new/' in response
    assert (f'href="/{translation.language}/article/translation/new/'
            not in response)
    assert f'value={translation.original_article.language}' not in response


def test_translation_creation_requires_login(client, article):
    response = client.get(
        f'/fr/article/translation/new/?original={article.id}')
    assert response.status_code == HTTPStatus.FOUND
    assert ('/fr/login?next=%2Ffr%2Farticle%2Ftranslation%2F'
            in response.headers.get('Location'))


def test_translation_creation_required_parameters(client, user, article):
    login(client, user.email, 'password')
    response = client.get('/en/article/translation/new/')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    response = client.get(
        f'/en/article/translation/new/?original={article.id}$')
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
    response = client.post(f'/{language}/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            ('http://localhost'
             f'/{language}/article/translation/{translation.id}/'))
    assert (get_flashed_messages() ==
            ['Thanks! Your translation has been saved'])


def test_translation_creation_with_existing_tag(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    tag = Tag.objects.create(name='Sensational', language=language)
    data = {
        'title': 'title',
        'summary': 'summary',
        'body': 'body',
        'original': article.id,
        'language': language,
        'tag-1': tag.name
    }
    response = client.post(f'/{language}/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert (response.headers.get('Location') ==
            ('http://localhost'
             f'/{language}/article/translation/{translation.id}/'))
    assert (get_flashed_messages() ==
            ['Thanks! Your translation has been saved'])
    assert translation.tags == [tag]


def test_translation_creation_with_unknown_tag(app, client, user, article):
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'title',
        'summary': 'summary',
        'body': 'body',
        'original': article.id,
        'language': language,
        'tag-1': 'Sensational'
    }
    response = client.post(f'/{language}/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    tag = Tag.objects.get(name='Sensational', language=language)
    assert (response.headers.get('Location') ==
            ('http://localhost'
             f'/{language}/article/translation/{translation.id}/'))
    assert (get_flashed_messages() ==
            ['Thanks! Your translation has been saved'])
    assert translation.tags == [tag]


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
    response = client.post(f'/{language}/article/translation/new/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation = Translation.objects.first()
    assert translation.image_filename == '/articles/image-name.jpg'
    assert translation.image_url == '/articles/image-name.jpg'
    assert str(translation.image_path).endswith('/articles/image-name.jpg')


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
    response = client.get(f'/fr/article/translation/{translation.id}/')
    assert response.status_code == HTTPStatus.OK


def test_translation_access_have_original_article_link(client, translation):
    response = client.get(f'/fr/article/translation/{translation.id}/')
    assert ((f'Translated from '
             f'<a href="/en/article/draft/{translation.original_article.id}/">'
             f'article title') in response)


def test_translation_can_have_raw_summary(client, translation):
    response = client.get(f'/fr/article/translation/{translation.id}/')
    assert '<div class=summary><p>summary text</p></div>' in response
    assert '<meta name=description content="summary text">' in response


def test_translation_can_have_html_summary(client, translation):
    translation.modify(summary='<p>summary text</p>')
    response = client.get(f'/fr/article/translation/{translation.id}/')
    assert '<div class=summary><p>summary text</p></div>' in response
    assert '<meta name=description content="summary text">' in response


def test_translation_access_have_translator(client, translation):
    response = client.get(f'/fr/article/translation/{translation.id}/')
    translator = translation.translators[0]
    assert (f'by <a href="/fr/profile/testy-tester-{translator.id}/">'
            f'{translator}</a>' in response)


def test_translation_access_published_should_return_404(
        client, published_translation):
    response = client.get(
        f'/fr/article/translation/{published_translation.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_access_wrong_id_should_return_404(client, translation):
    response = client.get(f'/fr/article/translation/foo{translation.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_translation_update_should_display_form(client, user, translation):
    login(client, user.email, 'password')
    response = client.get(f'/fr/article/translation/{translation.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert ('<textarea id=body name=body required>body text</textarea>'
            in response)


def test_translation_update_requires_login(client, translation):
    response = client.get(f'/fr/article/translation/{translation.id}/edit/')
    assert response.status_code == HTTPStatus.FOUND
    assert ('/fr/login?next=%2Ffr%2Farticle%2Ftranslation%2F'
            in response.headers.get('Location'))


def test_translation_update_values_should_redirect(client, user, translation):
    login(client, user.email, 'password')
    data = {
        'title': 'Modified title',
        'summary': 'Modified summary',
        'body': 'Modified body',
    }
    response = client.post(
        f'/fr/article/translation/{translation.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.FOUND
    translation.reload()
    assert (response.headers.get('Location') ==
            f'http://localhost/fr/article/translation/{translation.id}/')
    assert translation.title == 'Modified title'
    assert (get_flashed_messages() ==
            ['Your translation was successfully updated.'])


def test_update_translation_with_tag(client, user, editor, tag, translation):
    login(client, editor.email, 'password')
    data = {
        'title': 'Modified title',
        'tag-1': tag.name
    }
    response = client.post(f'/fr/article/translation/{translation.id}/edit/',
                           data=data, follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert (get_flashed_messages() ==
            ['Your translation was successfully updated.'])
    translation.reload()
    assert translation.title == 'Modified title'
    tag = Tag.objects.get(name=tag.name, language=translation.language)
    assert translation.tags == [tag]


def test_update_translation_with_unkown_tag(client, user, editor, tag,
                                            translation):
    login(client, editor.email, 'password')
    data = {
        'title': 'Modified title',
        'tag-1': tag.name,
        'tag-2': 'Sensational'
    }
    response = client.post(f'/fr/article/translation/{translation.id}/edit/',
                           data=data, follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert (get_flashed_messages() ==
            ['Your translation was successfully updated.'])
    translation.reload()
    tag = Tag.objects.get(name=tag.name, language=translation.language)
    tag2 = Tag.objects.get(name='Sensational', language=translation.language)
    assert translation.tags == [tag, tag2]


def test_translation_published_should_return_200(
        client, published_translation):
    response = client.get(
        f'/fr/article/{published_translation.slug}-{published_translation.id}/'
    )
    assert response.status_code == HTTPStatus.OK


def test_translation_published_should_have_translator(
        client, published_translation):
    response = client.get(
        f'/fr/article/{published_translation.slug}-{published_translation.id}/'
    )
    translator = published_translation.translators[0]
    published_article = published_translation.original_article
    assert response.status_code == HTTPStatus.OK
    assert ((f'Translated from <a href="/en/article/'
             f'{published_article.slug}-{published_article.id}/">'
             f'article title') in response)
    assert (f'<a href="/fr/profile/testy-tester-{translator.id}/" '
            'class=translator-link>' in response)
    assert str(translator) in response


def test_translation_published_should_have_reference(
        client, published_translation):
    published_article = published_translation.original_article
    response = client.get(
        f'/en/article/{published_article.slug}-{published_article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert (('<li class=translated-language><a href='
             f'/fr/article/title-{published_translation.id}/>') in response)


def test_article_model_is_translated_in(app, translation):
    article = translation.original_article
    assert article.is_translated_in(translation.language)
    assert not article.is_translated_in('dummy')


def test_article_model_get_translation(app, translation):
    article = translation.original_article
    assert article.get_translation(translation.language) == translation
    assert article.get_translation('dummy') is None


def test_translation_editing_language_prevents_duplicates(app, translation):
    translation.language = translation.original_article.language
    with pytest.raises(mongoengine.errors.NotUniqueError) as error:
        translation.save()
    assert str(error.value) == 'This article already exists in this language.'


def test_translation_published_translation_links_defaults(
        app, published_translation):
    language = app.config['LANGUAGES'][2][0]
    translation_url = published_translation.get_published_translation_url
    published_article = published_translation.original_article
    assert translation_url(published_translation.language) is None
    assert translation_url(language) is None
    assert (translation_url(published_article.language) ==
            f'/en/article/{published_article.slug}-{published_article.id}/')


def test_translation_cant_update_author(client, published_translation, editor):
    login(client, editor.email, 'password')
    article = published_translation.original_article
    response = client.get(
        f'/{published_translation.language}/article'
        f'/{published_translation.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert '<select name=authors' not in response


def test_translation_can_update_translator(client, published_translation,
                                           editor, user2):
    login(client, editor.email, 'password')
    article = published_translation.original_article
    response = client.get(
        f'/{published_translation.language}/article'
        f'/{published_translation.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert '<select name=translators' in response


def test_translation_can_edit_translators(client, translation, editor, user2):
    assert translation.translators[0] != user2
    login(client, editor.email, 'password')
    data = {
        'title': translation.title,
        'summary': translation.summary,
        'body': translation.body,
        'translators': [user2.id],
    }
    response = client.post(
        f'/fr/article/translation/{translation.id}/edit/', data=data)
    translation.reload()
    assert translation.translators[0].id == user2.id


def test_create_draft_sends_email_to_editor(app, client, article, user, editor):
    mail.init_app(app)  # Re-load using test configuration.
    login(client, user.email, 'password')
    language = app.config['LANGUAGES'][1][0]
    data = {
        'title': 'title',
        'summary': 'summary',
        'body': 'body',
        'original': article.id
    }
    with mail.record_messages() as outbox:
        response = client.post(f'/{language}/article/translation/new/',
                               data=data)
        translation = Translation.objects.first()
        assert response.status_code == HTTPStatus.FOUND
        assert len(outbox) == 1
        assert outbox[0].recipients == [
            app.config['EDITOR_EMAILS'][translation.language]]
        assert outbox[0].subject == f'New article translation in {language}'
        assert (f'/{language}/article/translation/{translation.id}/'
                in outbox[0].body)
