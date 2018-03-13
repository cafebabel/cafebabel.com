import pytest

from flask_security.utils import hash_password

from cafebabel import create_app
from cafebabel.commands import auth_fixtures, drop_collections
from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag
from cafebabel.articles.translations.models import Translation
from cafebabel.users.models import User

test_app = create_app('config.TestingConfig')


def pytest_runtest_setup():
    auth_fixtures(test_app)
    ds = test_app.user_datastore
    with test_app.app_context():
        user = ds.create_user(email='user@example.com',
                              password=hash_password('password'))
        ds.activate_user(user)
        user2 = ds.create_user(email='user2@example.com',
                               password=hash_password('password'))
        ds.activate_user(user2)
        ds.commit()


def pytest_runtest_teardown():
    drop_collections()


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    ctx = test_app.app_context()
    ctx.push()

    def tearDown():
        ctx.pop()

    request.addfinalizer(tearDown)
    return test_app


@pytest.fixture
def user():
    return User.objects.get(email='user@example.com')


@pytest.fixture
def user2():
    return User.objects.get(email='user2@example.com')


@pytest.fixture
def editor():
    return User.objects.get(email=test_app.config['EDITOR_EMAILS']['en'])


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='Wonderful',
        summary='summary text',
        language=test_app.config['LANGUAGES'][0][0])


@pytest.fixture
def article(user):
    return Article.objects.create(
        title='article title',
        summary='summary text',
        authors=[user],
        language=test_app.config['LANGUAGES'][0][0],
        body='body text')


@pytest.fixture
def published_article(user):
    return Article.objects.create(
        title='article title',
        summary='summary text',
        authors=[user],
        language=test_app.config['LANGUAGES'][0][0],
        body='body text',
        status='published')


@pytest.fixture
def translation(user, article):
    language = test_app.config['LANGUAGES'][1][0]
    return Translation.objects.create(
        title='title',
        summary='summary text',
        language=language,
        body='body text',
        authors=[user],
        translators=[user.id],
        original_article=article.id)


@pytest.fixture
def published_translation(user, published_article):
    language = test_app.config['LANGUAGES'][1][0]
    return Translation.objects.create(
        title='title',
        summary='summary text',
        language=language,
        body='body text',
        authors=[user],
        translators=[user.id],
        original_article=published_article.id,
        status='published')
