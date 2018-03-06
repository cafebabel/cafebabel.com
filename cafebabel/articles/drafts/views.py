from flask import Blueprint, flash, redirect, render_template, request

from ...core.helpers import editor_required, current_language
from ...users.models import User
from ..models import Article

drafts = Blueprint('drafts', __name__)


@drafts.route('/')
@editor_required
def list():
    articles = Article.objects(status='draft').hard_limit()
    return render_template('articles/drafts/list.html', articles=articles)


@drafts.route('/new/', methods=['get', 'post'])
@editor_required
def create():
    if request.method == 'POST':
        article = Article().save_from_request(request)
        flash('Your article was successfully saved.')
        return redirect(article.detail_url)

    article = Article()
    authors = User.objects.all()
    return render_template('articles/drafts/create.html', article=article,
                           authors=authors)


@drafts.route('/<regex("\w{24}"):draft_id>/edit/', methods=['get', 'post'])
def edit(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    if request.method == 'POST':
        article.save_from_request(request)
        flash('Your article was successfully saved.')
        return redirect(article.detail_url)

    authors = User.objects.all()
    return render_template('articles/drafts/edit.html', article=article,
                           authors=authors)


@drafts.route('/<regex("\w{24}"):draft_id>/')
def detail(draft_id):
    article = Article.objects.get_or_404(id=draft_id, status='draft')
    return render_template('articles/drafts/detail.html', article=article)
