import pytest
from flask_security.confirmable import confirm_user

from cafebabel import create_app
from cafebabel.articles.models import Article
from cafebabel.articles.translations.models import Translation
from cafebabel.users.models import Role, User, UserProfile

test_app = create_app('config.TestingConfig')


def pytest_runtest_setup():
    Role.objects.create(name='editor')
    admin_role = Role.objects.create(name='admin')
    admin_user = test_app.user_datastore.create_user(
        email='admin@example.com', password='password')
    test_app.user_datastore.add_role_to_user(admin_user, admin_role)


def pytest_runtest_teardown():
    Role.drop_collection()
    User.drop_collection()
    Article.drop_collection()


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
