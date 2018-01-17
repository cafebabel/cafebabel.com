from http import HTTPStatus

from flask import abort, current_app
from flask_mongoengine import BaseQuerySet
from mongoengine import signals

from ... import db
from ...core.helpers import slugify
from ...core.mixins import UploadableImageMixin


class TagQuerySet(BaseQuerySet):

    def get_or_create(self, **kwargs):
        try:
            return self.get(**kwargs)
        except Tag.DoesNotExist:
            return self.create(**kwargs)


class Tag(db.Document, UploadableImageMixin):
    name = db.StringField(required=True)
    slug = db.StringField(required=True)
    language = db.StringField(max_length=2, required=True)
    summary = db.StringField()

    meta = {
        'queryset_class': TagQuerySet
    }

    def __str__(self):
        return f'{self.name} ({self.language})'

    @classmethod
    def update_slug(cls, sender, document, **kwargs):
        document.slug = slugify(document.name)

    def get_images_url(self):
        return current_app.config.get('TAGS_IMAGES_URL')

    def get_images_path(self):
        return current_app.config.get('TAGS_IMAGES_PATH')

    def save_from_request(self, request):
        data = request.form.to_dict()
        files = request.files
        if 'name' in data or 'language' in data:
            abort(HTTPStatus.BAD_REQUEST)
        for field, value in data.items():
            setattr(self, field, value)
        if data.get('delete-image'):
            self.delete_image()
        image = files.get('image')
        if image:
            self.attach_image(image)
        return self.save()


signals.pre_save.connect(Tag.update_slug, sender=Tag)
signals.post_save.connect(Tag.store_image, sender=Tag)
signals.pre_delete.connect(Tag.delete_image_file, sender=Tag)
