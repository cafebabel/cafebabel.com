from flask import Blueprint, flash, redirect, render_template, request

from ...core.helpers import current_language, editor_required
from ..models import Article

drafts = Blueprint('drafts', __name__)


@drafts.route('/')
@editor_required
def list():
    drafts = Article.objects.drafts(language=current_language()).hard_limit()
    return render_template('articles/drafts/list.html', drafts=drafts)


@drafts.route('/new/', methods=['get', 'post'])
@editor_required
def create():
    article = Article()
    if request.method == 'POST':
        article = article.save_from_request(request)
        flash('Your article has been saved as a draft.')
        return redirect(article.detail_url)
    return render_template('articles/drafts/create.html', article=article)


@drafts.route('/<regex("\w{24}"):draft_id>/edit/', methods=['get', 'post'])
@editor_required
def edit(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    if request.method == 'POST':
        article.save_from_request(request)
        flash('Your article was successfully updated.')
        return redirect(article.detail_url)
    return render_template('articles/drafts/edit.html', article=article)


@drafts.route('/<regex("\w{24}"):draft_id>/')
def detail(draft_id):
    article = Article.objects.get_or_404(id=draft_id, status='draft')
    return render_template('articles/drafts/detail.html', article=article)
