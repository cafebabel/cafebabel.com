from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...core.helpers import editor_required
from ...users.models import User
from ..models import Article

blueprint = Blueprint('draft', __name__)


@blueprint.route('/')
@editor_required
@login_required
def draft_create_form():
    article = Article()
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@blueprint.route('/', methods=['post'])
@editor_required
@login_required
def draft_create():
    article = Article._save_article(
        request.form.to_dict(), request.files, Article())
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@blueprint.route('/<regex("\w{24}"):draft_id>/edit/')
def draft_edit_form(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@blueprint.route('/<regex("\w{24}"):draft_id>/edit/', methods=['post'])
def draft_edit(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    article = Article._save_article(
        request.form.to_dict(), request.files, article)
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@blueprint.route('/<regex("\w{24}"):draft_id>/')
def draft_detail(draft_id):
    article = Article.objects.get_or_404(id=draft_id, status='draft')
    return render_template('articles/draft_detail.html', article=article)
