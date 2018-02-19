import datetime

from flask import url_for
from flask_login import current_user
from mongoengine import PULL, signals

from .. import db
from ..core.exceptions import ValidationError
from ..core.helpers import allowed_file, slugify
from ..core.mixins import UploadableImageMixin
from ..users.models import User
from .tags.models import Tag


class ArticleArchive(db.EmbeddedDocument):
    pk = db.IntField()  # In use for migrations (references in related).
    url = db.StringField()  # In use for redirections.
    relateds = db.ListField()


class Article(db.Document, UploadableImageMixin):
    title = db.StringField(required=True)
    slug = db.StringField(required=True)
    language = db.StringField(max_length=2, required=True)
    category = db.StringField()
    summary = db.StringField(required=True)
    body = db.StringField(required=True)
    status = db.StringField(default='draft')
    editor = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    author = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    publication_date = db.DateTimeField()
    tags = db.ListField(db.ReferenceField(Tag, reverse_delete_rule=PULL))
    archive = db.EmbeddedDocumentField(ArticleArchive)

    _translations = None

    meta = {
        'allow_inheritance': True,
        'indexes': ['archive.pk'],
        'ordering': ['-publication_date', '-creation_date']
    }

    def __str__(self):
        return self.title

    @property
    def upload_subpath(self):
        return 'articles'

    @property
    def detail_url(self):
        if self.is_draft:
            return url_for('drafts.detail', draft_id=self.id)
        else:
            return url_for('articles.detail', slug=self.slug,
                           article_id=self.id)

    @property
    def is_draft(self):
        return self.status == 'draft'

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def is_translation(self):
        return False

    def is_translated_in(self, language):
        return bool(self.get_translation(language))

    def get_translation(self, language):
        if not self._translations:
            from .translations.models import Translation  # NOQA: circular :/
            translations = Translation.objects(original_article=self).all()
            self._translations = {t.language: t for t in translations}
        return self._translations.get(language)

    @classmethod
    def update_publication_date(cls, sender, document, **kwargs):
        if document.is_published and not document.publication_date:
            document.publication_date = datetime.datetime.utcnow()

    @classmethod
    def update_slug(cls, sender, document, **kwargs):
        document.slug = slugify(document.title)

    def save_from_request(self, request):
        data = request.form.to_dict()
        files = request.files
        if current_user.has_role('editor'):
            if not self.editor:
                data['editor'] = current_user.id
            data['author'] = User.objects.get(id=data['author'])
        else:
            if data.get('author'):
                del data['author']
            if data.get('editor'):
                del data['editor']
        self.tags = []
        language = data.get('language')
        for field, value in data.items():
            if field.startswith('tag-') and value:
                tag = Tag.objects.get_or_create(name=value, language=language)
                if tag not in self.tags:
                    self.tags.append(tag)
            else:
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


signals.pre_save.connect(Article.update_publication_date, sender=Article)
signals.pre_save.connect(Article.update_slug, sender=Article)
signals.post_save.connect(Article.store_image, sender=Article)
signals.pre_delete.connect(Article.delete_image_file, sender=Article)
