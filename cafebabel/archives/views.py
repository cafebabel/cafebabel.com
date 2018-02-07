from http import HTTPStatus

from flask import Blueprint, redirect, request, url_for

from ..core.helpers import current_language

from ..articles.models import Article

archives = Blueprint('archives', __name__)


@archives.route('/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<_slug>.html')
def archive(**kwargs):
    article = Article.objects.get_or_404(archive__url=request.url)
    return redirect(url_for('articles.detail', slug=article.slug,
                            article_id=article.id, lang=article.language),
                    HTTPStatus.MOVED_PERMANENTLY)
