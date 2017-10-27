import click
from cafebabel.core import app
from cafebabel.users import user_datastore
from cafebabel.users.models import Role, User, UserProfile, UserRoles
from peewee import create_model_tables, drop_model_tables


tables = [User, UserProfile, Role, UserRoles]


def _initdb():
    _dropdb()
    create_model_tables(tables, fail_silently=True)
    Role.create(name='editor')
    admin_user = user_datastore.create_user(
        email='admin@example.com', password='password',
        firstname='Admin', lastname='Admin')
    admin_role = Role.create(name='admin')
    user_datastore.add_role_to_user(user=admin_user, role=admin_role)
    click.echo('DB intialized.')


def _dropdb():
    drop_model_tables(tables, fail_silently=True)
    click.echo('DB dropped.')


@app.cli.command()
def initdb():
    _initdb()
