from ..articles.tags.models import Tag
from ..core.helpers import articles_for_tag


def test_articles_for_tag_empty(app):
    assert not articles_for_tag('society')


def test_articles_for_tag_published(app, published_article):
    language = app.config['LANGUAGES'][0][0]
    society = Tag.objects.create(name='Society', language=language)
    published_article.modify(tags=[society])
    assert articles_for_tag('society')[0].id == published_article.id
    assert not articles_for_tag('society', exclude=published_article)


def test_articles_for_tag_not_only_published(app, published_article, article):
    language = app.config['LANGUAGES'][0][0]
    society = Tag.objects.create(name='Society', language=language)
    published_article.modify(tags=[society])
    article.modify(tags=[society])
    assert len(articles_for_tag('society')) == 1
    assert len(articles_for_tag('society', only_published=False)) == 2


def test_articles_for_tag_limit(app, published_article, article):
    language = app.config['LANGUAGES'][0][0]
    society = Tag.objects.create(name='Society', language=language)
    published_article.modify(tags=[society])
    article.modify(tags=[society])
    assert (articles_for_tag('society', limit=1, only_published=False) ==
            [published_article])
