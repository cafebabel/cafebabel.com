from pathlib import Path

import pytest
from flask_security.confirmable import confirm_user

from cafebabel import app as myapp
from cafebabel.articles.models import Article
from cafebabel.articles.translations.models import Translation
from cafebabel.core.commands import _dropdb, _initdb
from cafebabel.users.models import Role, User, user_datastore


def pytest_runtest_setup():
    _initdb()


def pytest_runtest_teardown():
    _dropdb()


@pytest.fixture
def app():
    myapp.config.from_pyfile(Path(__file__).parent / 'settings.tests.py')
    return myapp


@pytest.fixture
def user():
    user = User.objects.create(email='testy@example.com', password='secret')
    with myapp.app_context():
        confirm_user(user)
    return user


@pytest.fixture
def editor(user):
    editor_role = Role.objects.get(name='editor')
    user_datastore.add_role_to_user(user, editor_role)
    return user


@pytest.fixture
def admin():
    return User.objects.get(email='admin@example.com')


@pytest.fixture
def article():
    en = myapp.config['LANGUAGES'][0][0]
    return Article.objects.create(
        title='article title',
        summary='summary text',
        language=en,
        body='body text')


@pytest.fixture
def translation(user, article):
    fr = myapp.config['LANGUAGES'][1][0]
    return Translation.objects.create(
        title='title',
        summary='summary text',
        language=fr,
        body='body text',
        translator=user.id,
        original_article=article.id)
