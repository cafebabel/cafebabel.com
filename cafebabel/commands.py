import click

from cafebabel.users.models import Role, User
from cafebabel.articles.models import Article, Tag


def drop_collections():
    Role.drop_collection()
    User.drop_collection()
    Article.drop_collection()
    Tag.drop_collection()
    click.echo('Roles, Users, Articles and Tags dropped.')


def roles_fixtures(app):
    Role.objects.create(name='editor')
    admin_role = Role.objects.create(name='admin')
    admin_user = app.user_datastore.create_user(
        email='admin@example.com', password='password')
    app.user_datastore.add_role_to_user(admin_user, admin_role)
    click.echo('DB intialized.')
