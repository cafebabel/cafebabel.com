from http import HTTPStatus
from io import BytesIO
from pathlib import Path

from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag
from flask.helpers import get_flashed_messages

from .utils import login


def test_tag_basics(tag):
    assert tag.slug == 'wonderful'
    assert str(tag) == 'Wonderful (en)'


def test_tag_non_ascii_name(app):
    language = app.config['LANGUAGES'][0][0]
    tag = Tag.objects.create(name='\u4e2d\u56fd\u4e0e\u4e16\u754c',
                             language=language)
    assert tag.slug == 'zhong-guo-yu-shi-jie'


def test_tag_deleted_remove_article_reference(app, tag, article):
    language = app.config['LANGUAGES'][0][0]
    tag2 = Tag.objects.create(name='Sensational', language=language)
    article.modify(tags=[tag, tag2])
    assert Article.objects(tags__in=[tag]).count() == 1
    assert Article.objects(tags__all=[tag, tag2]).count() == 1
    tag2.delete()
    article.reload()
    assert article.tags == [tag]


def test_tag_suggest_basics(client, tag):
    response = client.get('/en/article/tag/suggest/?language=en&terms=wond')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'language': 'en',
        'name': 'Wonderful',
        'slug': 'wonderful',
        'summary': 'summary text'
    }]


def test_tag_suggest_many(client, app, tag):
    language = app.config['LANGUAGES'][0][0]
    Tag.objects.create(name='Wondering', language=language)
    response = client.get('/en/article/tag/suggest/?language=en&terms=wond')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'language': 'en',
        'name': 'Wonderful',
        'slug': 'wonderful',
        'summary': 'summary text'
    }, {
        'language': 'en',
        'name': 'Wondering',
        'slug': 'wondering',
        'summary': ''
    }]


def test_tag_only_language(client, app, tag):
    language = app.config['LANGUAGES'][1][0]
    Tag.objects.create(name='Wondering', language=language)
    response = client.get('/en/article/tag/suggest/?language=fr&terms=wond')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'language': 'fr',
        'name': 'Wondering',
        'slug': 'wondering',
        'summary': ''
    }]


def test_tag_suggest_too_short(client, tag):
    response = client.get('/en/article/tag/suggest/?language=en&terms=wo')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Suggestions are made available from 3-chars and more.' in response


def test_tag_suggest_wrong_language(client, tag):
    response = client.get('/en/article/tag/suggest/?language=ca&terms=wond')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert ("Languages available: ['en', 'fr', 'es', 'it', 'de', 'pl']"
            in response)


def test_tag_detail(app, client, tag, published_article):
    published_article.modify(tags=[tag])
    response = client.get('/en/article/tag/wonderful/')
    assert response.status_code == HTTPStatus.OK
    assert tag.name in response
    assert tag.summary in response
    assert (f'<a href={published_article.detail_url }>'
            f'{published_article.title}' in response)


def test_tag_detail_draft(client, tag, article):
    article.modify(tags=[tag])
    response = client.get('/en/article/tag/wonderful/')
    assert response.status_code == HTTPStatus.OK
    assert tag.name in response
    assert article.title not in response


def test_tag_detail_unknown(client, tag):
    response = client.get('/en/article/tag/sensational/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_tag_update_summary(app, client, tag, editor):
    login(client, editor.email, 'password')
    data = {'summary': 'custom summary'}
    response = client.post(f'/en/article/tag/{tag.slug}/edit/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your tag was successfully saved.']
    tag.reload()
    assert tag.summary == 'custom summary'


def test_tag_update_image(app, client, tag, editor):
    login(client, editor.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image_content = BytesIO(content.read())
    data = {
        'summary': 'custom summary',
        'image': (image_content, 'image-name.jpg'),
    }
    response = client.post(f'/en/article/tag/{tag.slug}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your tag was successfully saved.']
    tag.reload()
    assert tag.summary == 'custom summary'
    assert tag.image_filename == '/tags/image-name.jpg'
    assert Path(app.config.get('UPLOADS_FOLDER') /
                'tags' / 'image-name.jpg').exists()


def test_tag_update_image_unallowed_extension(app, client, tag, editor):
    login(client, editor.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image_content = BytesIO(content.read())
    data = {
        'summary': 'custom summary',
        'image': (image_content, 'image-name.zip'),
    }
    assert 'zip' not in app.config.get('ALLOWED_EXTENSIONS')
    response = client.post(f'/en/article/tag/{tag.slug}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == [
        'There was an error in your tag submission: Unallowed extension.'
    ]
    tag.reload()
    assert tag.image_filename is None
    assert not Path(app.config.get('UPLOADS_FOLDER') /
                    'tags' / 'image-name.zip').exists()


def test_tag_update_name_not_possible(app, client, tag, editor):
    login(client, editor.email, 'password')
    data = {'name': 'updated title'}
    response = client.post(f'/en/article/tag/{tag.slug}/edit/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_tag_update_language_not_possible(app, client, tag, editor):
    login(client, editor.email, 'password')
    data = {'language': app.config['LANGUAGES'][2][0]}
    response = client.post(f'/en/article/tag/{tag.slug}/edit/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_tag_categories(app, tag):
    language = app.config['LANGUAGES'][0][0]
    assert 'impact' in app.config['CATEGORIES_SLUGS']
    impact = Tag.objects.create(name='Impact', language=language)
    assert Tag.objects.categories(language=language)[0].slug == impact.slug
    assert impact.is_category


def test_tag_categories_by_language(app, tag):
    language1 = app.config['LANGUAGES'][0][0]
    language2 = app.config['LANGUAGES'][1][0]
    assert 'impact' in app.config['CATEGORIES_SLUGS']
    impact = Tag.objects.create(name='Impact', language=language1)
    assert not Tag.objects.categories(language=language2)
    assert Tag.objects.categories(language=language1)[0].slug == impact.slug


def test_tag_menu_categories_redirect(app, client):
    Tag.objects.create(name='Raw', summary='text chapo',
                       language=app.config['LANGUAGES'][0][0])
    response = client.get('/en/article/tag/raw/')
    assert response.status_code == HTTPStatus.OK
    assert '<a href=/fr/article/tag/raw/>FR</a></li>' in response


def test_tag_menu_regular_do_not_redirect(app, client, tag):
    response = client.get(f'/en/article/tag/{tag.slug}/')
    assert response.status_code == HTTPStatus.OK
    assert f'<a href=/fr/article/tag/{tag.slug}/>FR</a></li>' not in response
