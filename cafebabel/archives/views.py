from http import HTTPStatus

from flask import Blueprint, redirect, request

from ..articles.models import Article

archives = Blueprint('archives', __name__)


@archives.route('/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<slug>.html')
def archive(slug, **kwargs):
    try:
        article = Article.objects.get(archive__url__iendswith=request.path)
    except Article.DoesNotExist:
        article = Article.objects.get_or_404(status='published', slug=slug)
    return redirect(article.detail_url, HTTPStatus.MOVED_PERMANENTLY)
