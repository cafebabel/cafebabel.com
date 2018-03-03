import datetime

from flask import current_app, url_for
from flask_login import current_user
from flask_mongoengine import BaseQuerySet
from mongoengine import PULL, signals

from .. import db
from ..core.exceptions import ValidationError
from ..core.helpers import allowed_file, slugify
from ..core.mixins import UploadableImageMixin
from ..users.models import User
from .tags.models import Tag


class ArticleQuerySet(BaseQuerySet):

    def published(self, language):
        return self.filter(status='published', language=language)

    def hard_limit(self):
        return self[:current_app.config['HARD_LIMIT_PER_PAGE']]


class ArticleArchive(db.EmbeddedDocument):
    pk = db.IntField()  # In use for migrations (references in related).
    url = db.StringField()  # In use for redirections.
    relateds = db.ListField()


class Article(db.Document, UploadableImageMixin):
    title = db.StringField(required=True)
    slug = db.StringField(required=True)
    language = db.StringField(max_length=2, required=True)
    summary = db.StringField(required=True)
    body = db.StringField(required=True)
    status = db.StringField(default='draft')
    editor = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    authors = db.ListField(db.ReferenceField(User,
                                             reverse_delete_rule=db.PULL))
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    publication_date = db.DateTimeField()
    tags = db.ListField(db.ReferenceField(Tag, reverse_delete_rule=PULL))
    archive = db.EmbeddedDocumentField(ArticleArchive)

    _translations = None

    meta = {
        'queryset_class': ArticleQuerySet,
        'allow_inheritance': True,
        'indexes': ['archive.pk'],
        'ordering': ['-publication_date', '-creation_date']
    }

    def __str__(self):
        return self.title

    def __eq__(self, other):
        # We need to compare strings of primary keys because of mongo
        # duality of ObjectIDs vs. raw strings.
        return str(self.pk) == str(other.pk)

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

    @property
    def author(self):
        """
        This property and its setter below are temporary while the frontend
        only allows selecting one single author.
        """
        return self.authors and self.authors[0]

    @author.setter
    def author(self, value):
        if value in self.authors:
            self.authors.remove(value)
        self.authors.insert(0, value)

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
            data['authors'] = [
                User.objects.get(profile__name__exact=user.strip())
                for user in data['authors'].split(',') if user.strip()
            ]
        else:
            if data.get('authors'):
                del data['authors']
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
