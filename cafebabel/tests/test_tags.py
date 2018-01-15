from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag


def test_tag_basics(tag):
    assert tag.slug == 'a-tag'
    assert str(tag) == 'A tag (en)'


def test_tag_deleted_remove_article_reference(app, tag, article):
    language = app.config['LANGUAGES'][0][0]
    tag2 = Tag.objects.create(name='Tag two', language=language)
    article.modify(tags=[tag, tag2])
    assert Article.objects(tags__in=[tag]).count() == 1
    assert Article.objects(tags__all=[tag, tag2]).count() == 1
    tag2.delete()
    article.reload()
    assert article.tags == [tag]
