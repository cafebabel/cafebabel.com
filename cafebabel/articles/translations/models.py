from flask import url_for
from mongoengine import signals, ValidationError

from ... import app, db
from ...users.models import User
from ...articles.models import Article


class Translation(Article):
    translator = db.ReferenceField(User, required=True)
    original_article = db.ReferenceField('Article', required=True)

    @property
    def detail_url(self):
        if self.is_draft:
            return url_for('translations.detail', id=self.id)
        else:
            return url_for('articles.detail', slug=self.slug,
                           article_id=self.id)

    @property
    def is_translation(self):
        return True

    @property
    def image_url(self):
        if self.has_image:
            return (f'{app.config.get("ARTICLES_IMAGES_URL")}/'
                    f'{self.original_article.id}')

    def clean(self):
        super().clean()
        try:
            translations = Translation.objects.filter(
                original_article=self.original_article, language=self.language)
            if (translations and
                    (len(translations) > 1 or translations[0].id != self.id)):
                raise ValidationError('Existing translation already exists.')
        except Translation.DoesNotExist:
            pass
        try:
            Article.objects.get(id=self.original_article.id,
                                language=self.language)
            raise ValidationError('Original article in the same language.')
        except Article.DoesNotExist:
            pass


signals.pre_save.connect(Article.update_publication_date, sender=Translation)
signals.pre_save.connect(Article.update_slug, sender=Translation)
signals.post_save.connect(Article.store_image, sender=Translation)
signals.pre_delete.connect(Article.delete_image_file, sender=Translation)
