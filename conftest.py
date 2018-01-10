import pytest
from flask_security.confirmable import confirm_user

from cafebabel import create_app
from cafebabel.commands import drop_collections, roles_fixtures
from cafebabel.articles.models import Article, Tag
from cafebabel.articles.translations.models import Translation
from cafebabel.users.models import Role, User, UserProfile

test_app = create_app('config.TestingConfig')


def pytest_runtest_setup():
    roles_fixtures(test_app)


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
    user = User(email='testy@example.com', password='secret')
    user.profile = UserProfile()
    user.save()
    with test_app.app_context():
        confirm_user(user)
    user.reload()
    return user


@pytest.fixture
def editor():
    editor_role = Role.objects.get(name='editor')
    user = User(email='editor@example.com', password='secret')
    user.profile = UserProfile()
    user.save()
    with test_app.app_context():
        confirm_user(user)
    test_app.user_datastore.add_role_to_user(user, editor_role)
    return user


@pytest.fixture
def admin():
    return User.objects.get(email='admin@example.com')


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='Wildlife',
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
        translator=user.id,
        original_article=article.id)
