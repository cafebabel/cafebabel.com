from http import HTTPStatus

from flask import Blueprint, redirect, request, url_for

from ..articles.models import Article

archives = Blueprint('archives', __name__)


@archives.route('/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<_slug>.html')
def archive(**kwargs):
    archive_url = request.headers.get('Archive', request.url)
    article = Article.objects.get_or_404(archive__url=archive_url)
    redirect_to = url_for('articles.detail', slug=article.slug,
                          article_id=article.id, lang=article.language)
    return redirect(redirect_to, HTTPStatus.MOVED_PERMANENTLY)
