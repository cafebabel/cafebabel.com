from ..articles.tags.models import Tag
from ..core.helpers import articles_for_tag


def test_articles_for_tag_empty(app):
    tag, articles = articles_for_tag('society')
    assert tag is None
    assert not articles


def test_articles_for_tag_published(app, published_article):
    language = app.config['LANGUAGES'][0][0]
    society = Tag.objects.create(name='Society', language=language)
    published_article.modify(tags=[society])
    tag, articles = articles_for_tag('society')
    assert tag == society
    assert articles[0].id == published_article.id


def test_articles_for_tag_not_only_published(app, published_article, article):
    language = app.config['LANGUAGES'][0][0]
    society = Tag.objects.create(name='Society', language=language)
    published_article.modify(tags=[society])
    article.modify(tags=[society])
    tag, articles = articles_for_tag('society')
    assert tag == society
    assert len(articles) == 1
    tag, articles = articles_for_tag('society', only_published=False)
    assert tag == society
    assert len(articles) == 2


def test_articles_for_tag_limit(app, published_article, article):
    language = app.config['LANGUAGES'][0][0]
    society = Tag.objects.create(name='Society', language=language)
    published_article.modify(tags=[society])
    article.modify(tags=[society])
    tag, articles = articles_for_tag('society', limit=1, only_published=False)
    assert tag == society
    assert articles == [published_article]
