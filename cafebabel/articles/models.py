import datetime
from http import HTTPStatus

from flask import abort, url_for
from flask_login import current_user
from mongoengine import errors, queryset, signals

from .. import app, db
from ..core.helpers import slugify
from ..users.models import User


class ArticleQuerySet(queryset.QuerySet):

    def get_or_404(self, id, **extras):
        try:
            return self.get(id=id, **extras)
        except (Article.DoesNotExist, errors.ValidationError):
            abort(HTTPStatus.NOT_FOUND, 'No article matches this id.')


class Article(db.Document):
    title = db.StringField(required=True)
    slug = db.StringField(required=True)
    language = db.StringField(max_length=2, required=True)
    category = db.StringField()
    summary = db.StringField(required=True)
    body = db.StringField(required=True)
    has_image = db.BooleanField(default=False)
    status = db.StringField(default='draft')
    editor = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    author = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    publication_date = db.DateTimeField()
    _upload_image = None

    meta = {
        'allow_inheritance': True,
        'queryset_class': ArticleQuerySet
    }

    def __str__(self):
        return self.title

    @property
    def detail_url(self):
        if self.is_draft:
            return url_for('draft.draft_detail', draft_id=self.id)
        else:
            return url_for('article.article_detail',
                           slug=self.slug,
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

    @property
    def image_url(self):
        if self.has_image:
            return f'{app.config.get("ARTICLES_IMAGES_URL")}/{self.id}'

    def delete_image(self):
        if not self.has_image:
            return
        (app.config.get('ARTICLES_IMAGES_PATH') / str(self.id)).unlink()
        self.has_image = False
        self.save()

    def attach_image(self, image):
        self._upload_image = image

    @classmethod
    def update_publication_date(cls, sender, document, **kwargs):
        if document.is_published and not document.publication_date:
            document.publication_date = datetime.datetime.utcnow()

    @classmethod
    def update_slug(cls, sender, document, **kwargs):
        document.slug = slugify(document.title)

    @classmethod
    def store_image(cls, sender, document, **kwargs):
        if document._upload_image:
            document.has_image = True
            document._upload_image.save(
                str(app.config.get('ARTICLES_IMAGES_PATH') / str(document.id)))
            document._upload_image = None
            document.save()

    @classmethod
    def delete_image_file(cls, sender, document, **kwargs):
        document.delete_image()

    def _save_article(data, files, article):
        if current_user.has_role('editor'):
            if not article.editor:
                data['editor'] = current_user.id
            if data.get('author'):
                data['author'] = User.objects.get(id=data.get('author'))
        else:
            if data.get('author'):
                del data['author']
            if data.get('editor'):
                del data['editor']
        for field, value in data.items():
            setattr(article, field, value)
        if data.get('delete-image'):
            article.delete_image()
        image = files.get('image')
        if image:
            article.attach_image(image)
        return article.save()


signals.pre_save.connect(Article.update_publication_date, sender=Article)
signals.pre_save.connect(Article.update_slug, sender=Article)
signals.post_save.connect(Article.store_image, sender=Article)
signals.pre_delete.connect(Article.delete_image_file, sender=Article)
