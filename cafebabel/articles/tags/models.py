from http import HTTPStatus

from flask import abort, current_app, url_for
from flask_mongoengine import BaseQuerySet
from mongoengine import signals

from ... import db
from ...core.exceptions import ValidationError
from ...core.helpers import allowed_file, slugify
from ...core.mixins import UploadableImageMixin


class TagQuerySet(BaseQuerySet):

    def categories(self, language, **kwargs):
        return self.filter(slug__in=current_app.config['CATEGORIES_SLUGS'],
                           language=language)

    def get_or_create(self, **kwargs):
        try:
            return self.get(**kwargs)
        except Tag.DoesNotExist:
            return self.create(**kwargs)


class Tag(db.Document, UploadableImageMixin):
    name = db.StringField(required=True)
    slug = db.StringField(required=True)
    language = db.StringField(max_length=2, required=True, unique_with='slug')
    summary = db.StringField()

    meta = {
        'queryset_class': TagQuerySet
    }

    def __str__(self):
        return f'{self.name} ({self.language})'

    @classmethod
    def update_slug(cls, sender, document, **kwargs):
        if not document.slug:
            document.slug = slugify(document.name)

    @property
    def detail_url(self):
        return url_for('tags.detail', slug=self.slug, lang=self.language)

    @property
    def edit_url(self):
        return url_for('tags.edit', slug=self.slug, lang=self.language)

    @property
    def upload_subpath(self):
        return 'tags'

    @property
    def is_category(self):
        return self.name.lower() in current_app.config['CATEGORIES_SLUGS']

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
            if image.filename == '':
                raise ValidationError('No selected file.')
            if not allowed_file(image.filename):
                raise ValidationError('Unallowed extension.')
            self.attach_image(image)
        return self.save()


    @classmethod
    def clean_name(cls, sender, document, **kwargs):
        document.name = document.name.strip()


signals.pre_save.connect(Tag.clean_name, sender=Tag)
signals.pre_save.connect(Tag.update_slug, sender=Tag)
signals.post_save.connect(Tag.store_image, sender=Tag)
signals.pre_delete.connect(Tag.delete_image_file, sender=Tag)
