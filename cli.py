import click

from core import app, db, models


@app.cli.command()
def initdb():
    db.create_tables([
        models.User
    ])
    click.echo('DB intialized.')
