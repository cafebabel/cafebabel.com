from http import HTTPStatus

from flask import Blueprint, redirect, request, url_for

from ..articles.models import Article

archives = Blueprint('archives', __name__)


@archives.route('/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<_slug>.html')
def archive(**kwargs):
    # First deal with regular production redirections,
    # then fallback on redirections for preproduction.
    try:
        article = Article.objects.get(archive__url=request.url)
    except Article.DoesNotExist:
        # Only in use for preproduction testing, could be safely kept or
        # remove for production.
        archive_url = request.url.replace('http://preprod.cafebabel.',
                                          'http://www.cafebabel.')
        article = Article.objects.get_or_404(archive__url=archive_url)
    return redirect(url_for('articles.detail', slug=article.slug,
                            article_id=article.id),
                    HTTPStatus.MOVED_PERMANENTLY)
