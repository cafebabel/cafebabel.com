import click

from core import app
from core.models import Role, User, UserRoles


@app.cli.command()
def initdb():
    for Model in (Role, User, UserRoles):
        Model.drop_table(fail_silently=True)
        Model.create_table(fail_silently=True)
    click.echo('DB intialized.')
