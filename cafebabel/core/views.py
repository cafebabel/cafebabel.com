from flask import (Blueprint, current_app, render_template,
                   send_from_directory, request, redirect, url_for)
from http import HTTPStatus

from ..articles.models import Article
from ..articles.translations.models import Translation


cores = Blueprint('cores', __name__)


@cores.route('/')
def home():
    return render_template('home.html')


@cores.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(current_app.config['UPLOADS_FOLDER'], filename)


@cores.route('/<regex("[a-z-]+"):_tag>/<regex("[a-z]+"):_>/<_slug>.html')
def archive(**kwargs):
    article = Article.objects.get_or_404(archive__url=request.url)
    return redirect(url_for('articles.detail', slug=article.slug,
                            article_id=article.id),
                    HTTPStatus.MOVED_PERMANENTLY)
