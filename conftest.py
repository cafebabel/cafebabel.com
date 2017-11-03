import pytest
from cafebabel import app as myapp
from cafebabel.articles.models import Article
from cafebabel.core.commands import _dropdb, _initdb
from cafebabel.users.models import User
from flask_security.confirmable import confirm_user


def pytest_runtest_setup():
    _initdb()


def pytest_runtest_teardown():
    _dropdb()


@pytest.fixture
def app():
    myapp.config['MONGODB_DB'] = 'tests'
    myapp.config['WTF_CSRF_ENABLED'] = False
    return myapp


@pytest.fixture
def user():
    user = User.objects.create(email='testy@example.com', password='secret')
    with myapp.app_context():
        confirm_user(user)
    return user


@pytest.fixture
def admin():
    return User.objects.get(email='admin@example.com')


@pytest.fixture
def article():
    return Article.objects.create(
        title='title',
        language=myapp.config['LANGUAGES'][0][0],
        body='body')
