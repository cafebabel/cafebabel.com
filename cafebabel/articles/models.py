import datetime

from peewee import DateTimeField, CharField, ForeignKeyField

from .. import db
from ..users.models import User


class Article(db.Model):
    title = CharField(null=False)
    slug = CharField(null=False)
    language = CharField(max_length=2, null=False)
    category = CharField(null=True)
    summary = CharField(null=True)
    body = CharField(null=True)
    image = CharField(null=True)
    status = CharField(default='draft')
    editor = ForeignKeyField(User, related_name='edits')
    author = ForeignKeyField(User, related_name='articles')
    creation_date = DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return self.title
