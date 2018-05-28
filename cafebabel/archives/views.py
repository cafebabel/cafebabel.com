from http import HTTPStatus

from flask import Blueprint, redirect, request

from ..articles.models import Article

archives = Blueprint('archives', __name__)


@archives.route('/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<_slug>.html')
@archives.route('/<regex("[a-z-]{2}"):_lang>/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<_slug>.html')
@archives.route('/<regex("[a-z-]{2}"):_lang>/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_article>/<regex("[a-z]+"):_>/<_slug>.html')
def archive(**kwargs):
    article = Article.objects.get_or_404(archive__url__iendswith=request.path)
    return redirect(article.detail_url, HTTPStatus.MOVED_PERMANENTLY)
