import mongoengine
from werkzeug.routing import BaseConverter, ValidationError

from ..articles.models import Article


class ArticleConverter(BaseConverter):

    def __init__(self, url_map, status):
        super(ArticleConverter, self).__init__(url_map)
        self.status = status

    def to_python(self, value):
        if '-' not in value:
            raise ValidationError()

        values = value.split('-')
        article_id = values[-1]
        article_slug = '-'.join(values[:-1])
        try:
            article = Article.objects.get(id=article_id, status=self.status)
        except (Article.DoesNotExist, mongoengine.errors.ValidationError):
            raise ValidationError()
        article.url_slug = article_slug  # Attach for future test, not saved.
        return article

    def to_url(self, article):
        return f'{article.slug}-{article.id}'
