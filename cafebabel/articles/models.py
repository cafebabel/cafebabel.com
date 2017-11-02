import datetime
import os
from hashlib import md5
from pathlib import Path

from peewee import DateTimeField, CharField, ForeignKeyField
from playhouse.signals import pre_save, post_save

from .. import app, db
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
    _upload_image = None

    def __str__(self):
        return self.title

    @property
    def is_draft(self):
        return self.status == 'draft'

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def image_url(self):
        if self.image:
            return f'{app.config.get("ARTICLES_IMAGES_URL")}/{self.image}'

    def delete_image(self):
        if not self.image:
            return
        Path(f'{app.config.get("ARTICLES_IMAGES_PATH")}/{self.image}').unlink()
        self.image = None
        self.save()

    def attach_image(self, image):
        if not image:
            return
        self._upload_image = image


@pre_save(sender=Article)
def publication_status_changed(ModelClass, instance, created):
    if instance.status == 'published' and not instance.publication_date:
        instance.publication_date = datetime.datetime.utcnow()


@pre_save(sender=Article)
def create_article_slug(ModelClass, instance, created):
    instance.slug = slugify(instance.title)
    if not instance.uid:
        instance.uid = os.urandom(16).hex()


@post_save(sender=Article)
def store_image(ModelClass, instance, created):
    if instance._upload_image:
        instance.image = instance.id
        instance._upload_image.save(
            f'{app.config.get("ARTICLES_IMAGES_PATH")}/{instance.image}')
        instance._upload_image = None
        instance.save()
