import click

from .. import app
from ..users.models import Role, User, user_datastore


def _initdb():
    _dropdb()
    Role.objects.create(name='editor')
    admin_role = Role.objects.create(name='admin')
    admin_user = user_datastore.create_user(
        email='admin@example.com', password='password')
    user_datastore.add_role_to_user(admin_user, admin_role)
    click.echo('DB intialized.')


def _dropdb():
    Role.drop_collection()
    User.drop_collection()
    click.echo('Roles and Users dropped.')


@app.cli.command()
def initdb():
    _initdb()
