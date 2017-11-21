from http import HTTPStatus

import mongoengine
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, fresh_login_required, login_required
from flask_mail import Message

from .. import app, mail
from ..core.helpers import editor_required
from ..users.models import User
from .models import Article


proposal_bp = Blueprint(
    'proposal', __name__, template_folder='templates/articles')
draft_bp = Blueprint(
    'draft', __name__, template_folder='templates/articles')
article_bp = Blueprint(
    'article', __name__, template_folder='templates/articles')


def _save_article(data, article):
    if current_user.has_role('editor'):
        if not article.editor:
            data['editor'] = current_user.id
        if data.get('author'):
            data['author'] = User.objects.get(id=data.get('author'))
    else:
        if data.get('author'):
            del data['author']
        if data.get('editor'):
            del data['editor']
    for field, value in data.items():
        setattr(article, field, value)
    if data.get('delete-image'):
        article.delete_image()
    image = request.files.get('image')
    if image:
        article.attach_image(image)
    return article.save()


@proposal_bp.route('/')
def proposal_create_form():
    return render_template('articles/proposal.html')


@proposal_bp.route('/', methods=['post'])
def proposal_create():
    data = request.form
    msg = Message(f'Article proposal: {data["topic"]}',
                  sender=data['email'],
                  recipients=[
                      app.config['EDITOR_EMAILS'][data.get('language', 'en')]
                  ],
                  body=f'''
Language: {{data['language']}}
Name: {data['name']}
Email: {{data['email']}}
city: {{data['city']}}
topic: {data['topic']}
Angle: {data['angle']}
Media: {data['media']}
Format: {data['format']}
Section: {data['section']}
Additional infos: {data['additional']}
                  ''',
                  )
    mail.send(msg)
    flash('Your proposal was successfully send.', 'success')
    return redirect(url_for('home'))


@draft_bp.route('/')
@editor_required
@login_required
def draft_create_form():
    article = Article()
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@draft_bp.route('/', methods=['post'])
@editor_required
@login_required
def draft_create():
    article = _save_article(request.form.to_dict(), Article())
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@draft_bp.route('/<regex("\w{24}"):draft_id>/edit/')
def draft_edit_form(draft_id):
    try:
        article = Article.objects.get(id=draft_id)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this id.')
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@draft_bp.route('/<regex("\w{24}"):draft_id>/edit/',
                methods=['post'])
def draft_edit(draft_id=None):
    try:
        article = Article.objects.get(id=draft_id)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this id.')
    article = _save_article(request.form.to_dict(), article)
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@draft_bp.route('/<regex("\w{24}"):draft_id>/')
def draft_detail(draft_id):
    try:
        article = Article.objects.get(id=draft_id, status='draft')
    except Article.DoesNotExist:
        abort(404, 'No draft found with this id.')
    return render_template('articles/draft_detail.html', article=article)


# Only route with the slug for SEO purpose.
@article_bp.route('/<slug>-<regex("\w{24}"):article_id>/')
def article_detail(slug, article_id):
    try:
        article = Article.objects.get(id=article_id, status='published')
    except Article.DoesNotExist:
        abort(HTTPStatus.NOT_FOUND, 'No article matches this id.')
    if article.slug != slug:
        return redirect(
            url_for('.article_detail', article_id=article.id,
                    slug=article.slug),
            code=HTTPStatus.MOVED_PERMANENTLY)
    return render_template('articles/detail.html', article=article)


@article_bp.route('/<regex("\w{24}"):article_id>/', methods=['post'])
@login_required
@editor_required
def article_edit(article_id):
    try:
        article = Article.objects.get(id=article_id, status='published')
    except (Article.DoesNotExist, mongoengine.errors.ValidationError):
        abort(HTTPStatus.NOT_FOUND, 'No article matches this id.')
    article = _save_article(request.form.to_dict(), article)
    flash('Your article was successfully saved.')
    return redirect(
        url_for('.article_detail', article_id=article.id, slug=article.slug))


@article_bp.route('/<regex("\w{24}"):article_id>/form/')
@login_required
@editor_required
def article_edit_form(article_id):
    try:
        article = Article.objects.get(id=article_id, status='published')
    except (Article.DoesNotExist, mongoengine.errors.ValidationError):
        abort(HTTPStatus.NOT_FOUND, 'No article matches this id.')
    authors = User.objects.all()
    return render_template(
        'articles/edit.html', article=article, authors=authors)


@article_bp.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def article_delete(article_id):
    try:
        article = Article.objects.get(id=article_id)
    except (Article.DoesNotExist, mongoengine.errors.ValidationError):
        abort(HTTPStatus.NOT_FOUND, 'No article found with this id.')
    article.delete()
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))
