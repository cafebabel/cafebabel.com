import click
from auth import user_datastore
from core import app
from core.models import Role, User, UserRoles, UserProfile


@app.cli.command()
def initdb():
    for Model in (Role, User, UserRoles, UserProfile):
        Model.drop_table(fail_silently=True)
        Model.create_table(fail_silently=True)
    user_datastore.create_user(
        email='admin@example.com', password='password',
        firstname='Admin', lastname='Admin')
    click.echo('DB intialized.')
