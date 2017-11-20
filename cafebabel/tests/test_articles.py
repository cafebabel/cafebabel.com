from http import HTTPStatus
from pathlib import Path
from io import BytesIO

from flask import request, url_for
from flask.helpers import get_flashed_messages

from ..articles.models import Article
from .utils import login
from .. import app


def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/proposal/')
    assert response.status_code == 200
    assert 'action=/proposal/' in response.get_data(as_text=True)


def test_create_draft_should_display_form(client, editor):
    login(client, editor.email, 'secret')
    response = client.get('/draft/')
    assert response.status_code == 200
    assert '<input id=title' in response.get_data(as_text=True)


def test_create_draft_should_generate_article(client, editor):
    login(client, editor.email, 'secret')
    response = client.post('/draft/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
    }, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert '<h1>Test article</h1>' in body
    assert '<p>Article body</p>' in body


def test_create_published_draft_should_display_article(client, editor):
    login(client, editor.email, 'secret')
    response = client.post('/draft/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'status': 'published',
    }, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert request.url_rule.endpoint == 'article.article_detail'
    assert '<h1>Test article</h1>' in body
    assert '<p>Article body</p>' in body


def test_draft_editing_should_update_content(client, editor):
    login(client, editor.email, 'secret')
    data = {
        'title': 'My article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
    }
    draft = Article.objects.create(**data)
    updated_data = data.copy()
    updated_data['language'] = 'fr'
    response = client.post(f'/draft/{draft.id}/edit/',
                           data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    updated_draft = Article.objects.get(id=draft.id)
    assert updated_draft.id == draft.id
    assert updated_draft.language == 'fr'
    assert updated_draft.title == 'My article'


def test_draft_image_should_save_and_render(client, editor):
    login(client, editor.email, 'secret')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image = BytesIO(content.read())
    data = {
        'title': 'My article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'image': (image, 'image-name.jpg'),
    }
    response = client.post('/draft/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    article = Article.objects.first()
    assert article.has_image
    assert Path(app.config.get('ARTICLES_IMAGES_PATH') /
                str(article.id)).exists()
    assert f'<img src="{article.image_url}"' in response.get_data(as_text=True)


def test_draft_should_not_offer_social_sharing(client, article):
    response = client.get(f'/draft/{article.id}/')
    assert response.status_code == 200
    assert 'facebook.com/sharer' not in response.get_data(as_text=True)


def test_published_article_should_offer_social_sharing(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == 200
    assert 'facebook.com/sharer' in response.get_data(as_text=True)


def test_visitor_cannot_change_editor_nor_author(client, editor, user,
                                                 article):
    article.modify(status='draft', author=user, editor=editor)
    client.post(f'/draft/{article.id}/edit/', data={
        'title': 'Updated draft',
        'author': editor,
    })
    article.reload()
    assert article.title == 'Updated draft'
    assert article.author == user
    assert article.editor == editor


def test_access_published_article_should_return_200(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_published_draft_should_return_404(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/draft/{article.id}/')
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
    response = client.get(f'/article/{article.id}/form/')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_access_published_article_form_should_return_200(client, editor,
                                                         article):
    login(client, editor.email, 'secret')
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.id}/form/')
    assert response.status_code == HTTPStatus.OK


def test_access_draft_article_form_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.get(f'/article/{article.id}/form/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_article_form_should_return_404(client, editor):
    login(client, editor.email, 'secret')
    response = client.get(f'/article/foobarbazquxquuxquuzcorg/form/')
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
    response = client.post(f'/article/{article.id}/', data=data,
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
    response = client.post(f'/article/{article.id}/', data=data,
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
    response = client.post(f'/article/{article.id}/', data=data)
    assert response.status_code == HTTPStatus.FORBIDDEN
    article.reload()
    assert article.title == 'title'


def test_update_unpublished_article_should_return_404(client, user, editor,
                                                      article):
    login(client, editor.email, 'secret')
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/', data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    article.reload()
    assert article.title == 'title'


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
