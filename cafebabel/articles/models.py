import datetime
import os

from peewee import DateTimeField, CharField, ForeignKeyField
from playhouse.signals import pre_save

from .. import db
from ..core.helpers import slugify
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
    uid = CharField(max_length=32, null=False)
    editor = ForeignKeyField(User, related_name='edits')
    author = ForeignKeyField(User, related_name='articles')
    creation_date = DateTimeField(default=datetime.datetime.utcnow)
    publication_date = DateTimeField(null=True)

    def __str__(self):
        return self.title


@pre_save(sender=Article)
def publication_status_changed(ModelClass, instance, created):
    if instance.status == 'published' and not instance.publication_date:
        instance.publication_date = datetime.datetime.utcnow()


@pre_save(sender=Article)
def create_article_slug(ModelClass, instance, created):
    instance.slug = slugify(instance.title)
    if not instance.uid:
        instance.uid = os.urandom(16).hex()
