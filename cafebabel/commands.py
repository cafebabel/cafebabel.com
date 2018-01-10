import click
from flask_security.utils import hash_password

from cafebabel.users.models import Role, User
from cafebabel.articles.models import Article, Tag

from .fixtures import ARTICLES


def drop_collections():
    Role.drop_collection()
    User.drop_collection()
    Article.drop_collection()
    Tag.drop_collection()
    click.echo('Roles, Users, Articles and Tags dropped.')


def users_fixtures(ds):
    user = ds.create_user(email='user@example.com',
                          password=hash_password('password'))
    ds.activate_user(user)
    user2 = ds.create_user(email='user2@example.com',
                           password=hash_password('password'))
    ds.activate_user(user2)
    editor = ds.create_user(email='editor@example.com',
                            password=hash_password('password'))
    ds.activate_user(editor)
    click.echo('Users intialized.')


def roles_fixtures(ds):
    editor_role = Role.objects.create(name='editor')
    editor = User.objects.get(email='editor@example.com')
    ds.add_role_to_user(editor, editor_role)
    click.echo('Roles intialized.')


def auth_fixtures(app):
    ds = app.user_datastore
    with app.app_context():
        users_fixtures(ds)
        roles_fixtures(ds)
        ds.commit()
    click.echo('Auth intialized.')


def articles_fixtures(app):
    user = User.objects.get(email='user@example.com')
    editor = User.objects.get(email='editor@example.com')
    for ARTICLE in ARTICLES:
        Article.objects.create(
            title=ARTICLE['title'],
            summary=ARTICLE['summary'],
            author=user,
            editor=editor,
            language=app.config['LANGUAGES'][0][0],
            body=ARTICLE['body'])
    click.echo('Articles intialized.')
