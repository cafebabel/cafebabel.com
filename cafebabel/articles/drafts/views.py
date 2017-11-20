from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...core.helpers import editor_required
from ...users.models import User
from ..models import Article

blueprint = Blueprint('draft', __name__)


@blueprint.route('/new/', methods=['get', 'post'])
@editor_required
@login_required
def create():
    if request.method == 'POST':
        article = Article._save_article(
            request.form.to_dict(), request.files, Article())
        flash('Your article was successfully saved.')
        return redirect(article.detail_url)

    article = Article()
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@blueprint.route('/<regex("\w{24}"):draft_id>/edit/', methods=['get', 'post'])
def edit(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    if request.method == 'POST':
        article = Article._save_article(
            request.form.to_dict(), request.files, article)
        flash('Your article was successfully saved.')
        return redirect(article.detail_url)

    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@blueprint.route('/<regex("\w{24}"):draft_id>/')
def detail(draft_id):
    article = Article.objects.get_or_404(id=draft_id, status='draft')
    return render_template('articles/draft_detail.html', article=article)
