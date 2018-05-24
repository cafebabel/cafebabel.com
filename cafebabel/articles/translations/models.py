from flask import url_for
from flask_login import current_user
from mongoengine import signals, errors, ValidationError

from ... import db
from ...users.models import User
from ...articles.models import Article
from ...articles.tags.models import Tag
from ...core.helpers import current_language


class Translation(Article):
    translators = db.ListField(db.ReferenceField(User, required=True))
    original_article = db.ReferenceField('Article', required=True)

    @property
    def detail_url(self):
        if self.is_draft:
            return url_for('translations.detail', id=self.id,
                           lang=self.language)
        else:
            return url_for('articles.detail', slug=self.slug,
                           article_id=self.id, lang=self.language)

    @property
    def is_translation(self):
        return True

    def clean(self):
        super().clean()
        try:
            Article.objects.get(id=self.original_article.id,
                                language=self.language)
            raise ValidationError('Original article in the same language.')
        except Article.DoesNotExist:
            pass

    @classmethod
    def check_duplicate(cls, sender, document, **kwargs):
        first = Translation.objects(original_article=document.original_article,
                                    language=document.language).first()
        if ((first and first != document) or
                document.language == document.original_article.language):
            raise errors.NotUniqueError(
                'This article already exists in this language.')
        return document

    def save_from_request(self, request):
        data = request.form.to_dict()
        article = (self.original_article or
                   Article.objects.get_or_404(id=data.pop('original')))
        self.editor = self.editor or article.editor
        self.authors = self.authors or article.authors
        self.translators = self.translators or [current_user.id]
        self.original_article = article
        self.status = self.status or 'draft'
        self.image_filename = self.image_filename or article.image_filename
        self.tags = []

        data['language'] = self.language or current_language()
        for field, value in data.items():
            if field.startswith('tag-') and value:
                tag = Tag.objects.get_or_create(name=value,
                                                language=data['language'])
                if tag not in self.tags:
                    self.tags.append(tag)
            else:
                setattr(self, field, value)

        if current_user.has_role('editor'):
            self.translators = [
                User.objects.get(id=id_)
                for id_ in request.form.getlist('translators')
            ]

        return self.save()


signals.pre_save.connect(Article.update_publication_date, sender=Translation)
signals.pre_save.connect(Translation.check_duplicate, sender=Translation)
signals.pre_save.connect(Article.update_slug, sender=Translation)
signals.post_save.connect(Article.store_image, sender=Translation)
signals.pre_delete.connect(Article.delete_image_file, sender=Translation)
