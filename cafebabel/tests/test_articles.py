from http import HTTPStatus
from pathlib import Path
from io import BytesIO

from flask import url_for
from flask.helpers import get_flashed_messages

from ..articles.models import Article, Tag
from .utils import login


def test_access_published_article_should_return_200(client, published_article):
    response = client.get(f'/article/{published_article.slug}-'
                          f'{published_article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_article_with_large_slug_should_return_200(client,
                                                          published_article):
    published_article.slug = 'quite-large-slug-with-dashes'
    published_article.save()
    response = client.get(f'/article/{published_article.slug}-'
                          f'{published_article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_published_article_should_display_content(client, published_article,
                                                  user):
    published_article.author = user
    response = client.get(f'/article/{published_article.slug}-'
                          f'{published_article.id}/')
    assert response.status_code == 200
    assert f'<h1>{published_article.title}</h1>' in response
    assert f'<title>{published_article.title}' in response
    assert (f'<meta name=description content="{published_article.summary}"'
            in response)
    assert f'<p class=summary>{published_article.summary}</p>' in response
    assert f'<p>{published_article.body}</p>' in response
    assert (f'<time pubdate="{published_article.creation_date.date()}">'
            f'{published_article.creation_date.date()}</time>' in response)
    assert f'<span>{published_article.language}</span>' in response
    assert f'{published_article.author.profile.name}' in response
    assert (f'href="https://twitter.com/share?url=http%3A%2F%2Flocalhost%2F'
            f'article%2F{published_article.slug}-{published_article.id}%2F'
            f'&text={published_article.title}&via=cafebabel_eng"' in response)
    assert (f'href="https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2F'
            f'localhost%2Farticle%2F{published_article.slug}-'
            f'{published_article.id}%2F"' in response)
    assert '1 min' in response


def test_published_article_should_render_markdown(client, published_article):
    published_article.body = '## Body title\n> quote me'
    published_article.save()
    response = client.get(f'/article/{published_article.slug}-'
                          f'{published_article.id}/')
    assert response.status_code == 200
    assert f'<h1>{published_article.title}</h1>' in response
    assert f'<h2>Body title</h2>' in response
    assert f'<blockquote>\n<p>quote me</p>\n</blockquote>' in response


def test_access_no_article_should_return_404(client):
    response = client.get(f'/article/foo-bar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_id_should_return_404(client):
    response = client.get(f'/article/foobar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_old_slug_article_should_return_301(client, published_article):
    response = client.get(f'/article/wrong-slug-{published_article.id}/')
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY


def test_access_article_form_regular_user_should_return_403(client, user,
                                                            article):
    login(client, user.email, 'password')
    response = client.get(f'/article/{article.id}/edit/')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_access_published_article_form_should_return_200(client, editor,
                                                         published_article):
    login(client, editor.email, 'password')
    response = client.get(f'/article/{published_article.id}/edit/')
    assert response.status_code == HTTPStatus.OK


def test_access_no_article_form_should_return_404(client, editor):
    login(client, editor.email, 'password')
    response = client.get(f'/article/foobarbazquxquuxquuzcorg/edit/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_published_article_should_return_200(app, client, user, editor,
                                                    published_article):
    login(client, editor.email, 'password')
    data = {
        'title': 'updated',
        'author': user.id,
        'language': app.config['LANGUAGES'][1][0],
    }
    response = client.post(f'/article/{published_article.id}/edit/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your article was successfully saved.']
    published_article.reload()
    assert published_article.title == 'updated'
    assert published_article.author == user


def test_update_article_with_image_should_return_200(app, client, user, editor,
                                                     published_article):
    login(client, editor.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image_content = BytesIO(content.read())
    data = {
        'title': 'updated',
        'author': user.id,
        'image': (image_content, 'image-name.jpg'),
    }
    response = client.post(f'/article/{published_article.id}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your article was successfully saved.']
    published_article.reload()
    assert published_article.title == 'updated'
    assert published_article.author == user
    assert published_article.editor == editor
    assert published_article.has_image
    assert (Path(app.config.get('ARTICLES_IMAGES_PATH') /
                 str(published_article.id)).exists())


def test_update_article_with_user_should_return_403(client, user,
                                                    published_article):
    login(client, user.email, 'password')
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{published_article.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.FORBIDDEN
    published_article.reload()
    assert published_article.title == 'article title'


def test_update_unpublished_article_should_return_404(client, user, editor,
                                                      article):
    login(client, editor.email, 'password')
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    article.reload()
    assert article.title == 'article title'


def test_delete_article_should_return_200(client, editor, article):
    login(client, editor.email, 'password')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert Article.objects.all().count() == 0
    assert get_flashed_messages() == ['Article was deleted.']


def test_delete_article_regular_user_should_return_403(client, user, article):
    login(client, user.email, 'password')
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Article.objects.all().count() == 1


def test_delete_article_no_user_should_redirect(client, user, article):
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.FOUND
    assert '/login' in response.headers.get('Location')
    assert Article.objects.all().count() == 1


def test_delete_incorrect_id_should_return_404(client, editor, article):
    login(client, editor.email, 'password')
    response = client.post(f'/article/{article.id}foo/delete/')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Article.objects.all().count() == 1


def test_delete_inexistent_article_should_return_404(client, editor, article):
    article.delete()
    login(client, editor.email, 'password')
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_published_article_should_link_translations(client, article,
                                                           translation):
    article.status = 'published'
    article.save()
    translation.status = 'published'
    translation.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert ((f'<li class=translated-language><a href=/article/'
             f'title-{translation.id}/>fr</a></li>') in response)
    assert ((f'<li class=to-translate-languages>'
             f'<a href="{url_for("translations.create")}'
             f'?lang=es&original={article.id}">Español</a></li>') in response)


def test_article_should_know_its_translations(client, article, translation):
    assert article.is_translated_in(translation.language)
    assert not article.is_translated_in('es')


def test_article_to_translate_should_return_200(client):
    response = client.get(f'/article/to-translate/')
    assert response.status_code == HTTPStatus.OK


def test_article_to_translate_should_have_default_languages(client):
    response = client.get(f'/article/to-translate/')
    assert '<option value=en selected>English</option>' in response
    assert '<option value=fr selected>Français</option>' in response


def test_article_to_translate_should_filter_by_language(client):
    response = client.get(f'/article/to-translate/?from=fr&to=es')
    assert '<option value=fr selected>Français</option>' in response
    assert '<option value=es selected>Español</option>' in response


def test_article_to_translate_with_unknown_language(client):
    response = client.get(f'/article/to-translate/?from=xx@to=yy')
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_article_to_translate_should_have_translation_links(
        app, client, article):
    language = app.config['LANGUAGES'][1][0]
    article.modify(language=language)
    response = client.get(f'/article/to-translate/?from=fr&to=en')
    assert (f'href="/article/translation/new/'
            f'?lang=en&original={article.id}">Translate in English</a>'
            in response)
    assert (f'href="/article/translation/new/'
            f'?lang=fr&original={article.id}">Translate in Français</a>'
            not in response)


def test_translation_to_translate_should_not_have_original_language(
        client, article, translation):
    # Keep the `translation` fixture, even if not refered to.
    response = client.get(f'/article/to-translate/')
    assert (f'href=/article/translation/new/'
            f'?lang=en&original={article.id}>Translate in English</a>'
            not in response)
    assert (f'href=/article/translation/new/'
            f'?lang=fr&original={article.id}>Translate in Français</a>'
            not in response)


def test_translation_to_translate_should_have_original_language(
        app, client, article, translation):
    # Keep the `article` fixture, even if not refered to.
    language = app.config['LANGUAGES'][1][0]
    translation.modify(language=language)
    response = client.get(f'/article/to-translate/?from=fr&to=es')
    assert (f'href="/article/translation/new/'
            f'?lang=es&original={translation.original_article.id}">'
            f'Translate in Español</a>'
            in response)


def test_article_to_translate_should_have_only_other_links(
        app, client, article):
    language = app.config['LANGUAGES'][1][0]
    article.modify(language=language)
    response = client.get(f'/article/to-translate/?from=en&to=fr')
    assert 'Translate in ' not in response


def test_article_with_tag(app, tag, article):
    Article.objects(id=article.id).update_one(push__tags=tag)
    assert Article.objects(tags__in=[tag]).count() == 1
    article2 = Article.objects(tags__in=[tag]).first()
    assert article2.tags[0].summary == 'summary text'
    Article.objects(id=article.id).update_one(pull__tags=tag)
    assert Article.objects(tags__in=[tag]).count() == 0


def test_article_detail_contains_tags(client, app, tag, published_article):
    language = app.config['LANGUAGES'][0][0]
    tag2 = Tag.objects.create(name='Tag two', language=language)
    published_article.modify(tags=[tag, tag2])
    response = client.get(
        f'/article/{published_article.slug}-{published_article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert 'A tag, Tag two.' in response
