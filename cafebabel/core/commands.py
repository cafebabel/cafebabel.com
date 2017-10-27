import click
<<<<<<< HEAD:cafebabel/core/commands.py
=======
from cafebabel.core import app
from cafebabel.users import user_datastore
from cafebabel.users.models import Role, User, UserProfile, UserRoles
>>>>>>> providing editor granting checkbox to authorized users:cli.py
from peewee import create_model_tables, drop_model_tables

from .. import app, db
from ..users.models import Role, User, UserProfile, UserRoles, user_datastore

tables = [User, UserProfile, Role, UserRoles]


def _initdb():
    _dropdb()
    create_model_tables(tables, fail_silently=True)
    Role.create(name='editor')
    admin_user = user_datastore.create_user(
        email='admin@example.com', password='password',
        firstname='Admin', lastname='Admin')
    Role.create(name='editor')
    if not db.database.is_closed():
        db.close_db(None)
    click.echo('DB intialized.')


def _dropdb():
    drop_model_tables(tables, fail_silently=True)
    if not db.database.is_closed():
        db.close_db(None)
    click.echo('DB dropped.')


@app.cli.command()
def initdb():
    _initdb()
