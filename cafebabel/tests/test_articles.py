from http import HTTPStatus
from pathlib import Path
from io import BytesIO

from flask import url_for
from flask.helpers import get_flashed_messages

from ..articles.models import Article
from .utils import login
from .. import app


def test_published_article_should_offer_social_sharing(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == 200
    assert 'facebook.com/sharer' in response.get_data(as_text=True)


def test_access_published_article_should_return_200(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_published_draft_should_return_404(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/draft/{article.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_article_with_large_slug_should_return_200(client, article):
    article.status = 'published'
    article.slug = 'quite-large-slug-with-dashes'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_published_article_should_display_content(client, article, user):
    article.status = 'published'
    article.author = user
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert f'<h1>{article.title}</h1>' in content
    assert f'<title>{article.title}' in content
    assert f'<meta name=description content="{article.summary}"' in content
    assert f'<p class=summary>{article.summary}</p>' in content
    assert f'<p>{article.body}</p>' in content
    assert f'<time>{article.creation_date.date()}</time>' in content
    assert f'<span>{article.language}</span>' in content
    assert f'{article.author.profile.name}' in content
    assert (f'href="https://twitter.com/share?url=http%3A%2F%2Flocalhost%2F'
            f'article%2F{article.slug}-{article.id}%2F&text={article.title}'
            f'&via=cafebabel_eng"' in content)
    assert (f'href="https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2F'
            f'localhost%2Farticle%2F{article.slug}-{article.id}%2F"'
            in content)
    assert '1 min' in content


def test_published_article_should_render_markdown(client):
    article = Article.objects.create(title='My title',
                                     summary='Summary',
                                     body='## Body title\n> quote me',
                                     status='published', language='en')
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert f'<h1>{article.title}</h1>' in content
    assert f'<h2>Body title</h2>' in content
    assert f'<blockquote>\n<p>quote me</p>\n</blockquote>' in content


def test_access_draft_article_should_return_404(client, article):
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_article_should_return_404(client):
    response = client.get(f'/article/foo-bar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_id_should_return_404(client):
    response = client.get(f'/article/foobar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_old_slug_article_should_return_301(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/wrong-slug-{article.id}/')
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY


def test_access_article_form_regular_user_should_return_403(client, user,
                                                            article):
    login(client, user.email, 'secret')
    response = client.get(f'/article/{article.id}/edit/')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_access_published_article_form_should_return_200(client, editor,
                                                         article):
    login(client, editor.email, 'secret')
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.id}/edit/')
    assert response.status_code == HTTPStatus.OK


def test_access_draft_article_form_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.get(f'/article/{article.id}/edit/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_article_form_should_return_404(client, editor):
    login(client, editor.email, 'secret')
    response = client.get(f'/article/foobarbazquxquuxquuzcorg/edit/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_published_article_should_return_200(client, user, editor,
                                                    article):
    login(client, editor.email, 'secret')
    article.status = 'published'
    article.save()
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/edit/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your article was successfully saved.']
    article.reload()
    assert article.title == 'updated'
    assert article.author == user
    assert article.editor == editor


def test_update_article_with_image_should_return_200(client, user, editor,
                                                     article):
    login(client, editor.email, 'secret')
    article.status = 'published'
    article.save()
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image_content = BytesIO(content.read())
    data = {
        'title': 'updated',
        'author': user.id,
        'image': (image_content, 'image-name.jpg')
    }
    response = client.post(f'/article/{article.id}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your article was successfully saved.']
    article.reload()
    assert article.title == 'updated'
    assert article.author == user
    assert article.editor == editor
    assert article.has_image
    assert (Path(app.config.get('ARTICLES_IMAGES_PATH') / str(article.id))
            .exists())


def test_update_article_with_user_should_return_403(client, user, article):
    login(client, user.email, 'secret')
    article.status = 'published'
    article.save()
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.FORBIDDEN
    article.reload()
    assert article.title == 'article title'


def test_update_unpublished_article_should_return_404(client, user, editor,
                                                      article):
    login(client, editor.email, 'secret')
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/edit/', data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    article.reload()
    assert article.title == 'article title'


def test_delete_article_should_return_200(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert Article.objects.all().count() == 0
    assert get_flashed_messages() == ['Article was deleted.']


def test_delete_article_regular_user_should_return_403(client, user, article):
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Article.objects.all().count() == 1


def test_delete_incorrect_id_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Article.objects.all().count() == 1


def test_delete_inexistent_article_should_return_404(client, editor, article):
    article.delete()
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_published_article_should_link_translations(client, article,
                                                           translation):
    article.status = 'published'
    article.save()
    translation.status = 'published'
    translation.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    text = response.get_data(as_text=True)
    assert response.status_code == HTTPStatus.OK
    assert '<p>Translate this article in:</p>' in text
    assert ((f'<li><a href={url_for("translation.create")}'
             f'?lang=it&original={article.id}>Italiano</a></li>') in text)
    assert ((f'<li><a href={url_for("translation.create")}'
             f'?lang=fr&original={article.id}>Français</a></li>') not in text)


def test_article_should_know_its_translations(client, article, translation):
    assert article.is_translated_in(translation.language)
    assert not article.is_translated_in('es')


def test_article_to_translate_should_return_200(client):
    response = client.get(f'/article/to_translate/')
    assert response.status_code == HTTPStatus.OK


def test_article_to_translate_should_have_other_languages(client):
    response = client.get(f'/article/to_translate/')
    text = response.get_data(as_text=True)
    assert '<a href=/article/to_translate/?in=fr>Français</a>' in text
    assert '<a href=/article/to_translate/?in=en>English</a>' not in text


def test_article_to_translate_should_filter_by_language(client):
    response = client.get(f'/article/to_translate/?in=fr')
    text = response.get_data(as_text=True)
    assert '<a href=/article/to_translate/?in=fr>Français</a>' not in text
    assert '<a href=/article/to_translate/?in=en>English</a>' in text


def test_article_to_translate_should_have_translation_links(client, article):
    french = app.config['LANGUAGES'][1][0]
    article.modify(language=french)
    response = client.get(f'/article/to_translate/')
    text = response.get_data(as_text=True)
    assert (f'<a href=/article/translation/new/'
            f'?lang=en&original={article.id}>Translate in English</a>' in text)
    assert (f'<a href=/article/translation/new/'
            f'?lang=fr&original={article.id}>Translate in Français</a>'
            not in text)


def test_article_to_translate_should_have_only_other_links(client, article):
    french = app.config['LANGUAGES'][1][0]
    article.modify(language=french)
    response = client.get(f'/article/to_translate/?in=fr')
    text = response.get_data(as_text=True)
    assert 'Translate in ' not in text
