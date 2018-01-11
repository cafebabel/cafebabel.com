import pytest

from cafebabel import create_app
from cafebabel.commands import auth_fixtures, drop_collections
from cafebabel.articles.models import Article, Tag
from cafebabel.articles.translations.models import Translation
from cafebabel.users.models import User

test_app = create_app('config.TestingConfig')


def pytest_runtest_setup():
    auth_fixtures(test_app)


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
def editor():
    return User.objects.get(email='editor@example.com')


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='A tag',
        summary='summary text',
        language=test_app.config['LANGUAGES'][0][0])


@pytest.fixture
def article(user):
    return Article.objects.create(
        title='article title',
        summary='summary text',
        author=user,
        language=test_app.config['LANGUAGES'][0][0],
        body='body text')


@pytest.fixture
def published_article(user):
    return Article.objects.create(
        title='article title',
        summary='summary text',
        author=user,
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
        author=user,
        translator=user.id,
        original_article=article.id)
