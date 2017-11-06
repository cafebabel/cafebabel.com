from http import HTTPStatus

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, fresh_login_required, login_required
from flask_mail import Message

from .. import app, mail
from ..core.helpers import editor_required
from ..users.models import User
from .models import Article


article = Blueprint('article', __name__, template_folder='templates/articles')


@app.route('/article/proposal/')
def article_proposal():
    return render_template('articles/proposal.html')


@app.route('/article/proposal/', methods=['post'])
def article_proposal_create():
    data = request.form
    msg = Message(f'Article proposal: {data["topic"]}',
                  sender=data['email'],
                  recipients=[
                      app.config['EDITOR_EMAILS'][data.get('language', 'en')]
                  ],
                  body=f'''
Name: {data['name']}
City: {data['city']}
Angle: {data['angle']}
Format: {data['format']}
Additional infos: {data['additional']}
                  ''',
                  )
    mail.send(msg)
    flash('Your proposal was successfully send.', 'success')
    return redirect(url_for('home'))


@app.route('/article/draft/')
@editor_required
@login_required
def article_draft_new():
    article = Article()
    authors = User.objects.all()
    return render_template('articles/draft_edit.html', article=article,
                           authors=authors)


@app.route('/article/draft/<uid>/edit/')
def article_draft_edit(uid):
    try:
        article = Article.objects.get(uid=uid)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this uid.')
    authors = User.objects.all()
    return render_template('articles/draft_edit.html', article=article,
                           authors=authors)


@app.route('/article/draft/', methods=['post'])
@app.route('/article/draft/<uid>/edit/', methods=['post'])
def article_draft_save(uid=None):
    article = (Article.objects.get(uid=uid, status='draft')
               if uid else Article())
    image = request.files.get('image')
    data = request.form.to_dict()

    data['editor'] = current_user.id
    if data.get('author'):
        data['author'] = User.objects.get(id=data.get('author'))
    for field, value in data.items():
        setattr(article, field, value)
    if data.get('delete-image'):
        article.delete_image()
    if image:
        article.attach_image(image)
    article = article.save()

    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('article_draft_detail', uid=article.uid))
    else:
        return redirect(url_for('article_detail', slug=article.slug,
                                id=article.id))


@app.route('/article/draft/<uid>/')
def article_draft_detail(uid):
    try:
        article = Article.objects.get(uid=uid)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this uid.')
    return render_template('articles/draft_detail.html', article=article)


@app.route('/article/create/', methods=['post'])
@login_required
def article_create():
    image = request.files.get('image')
    data = request.form.to_dict()
    data['author'] = User.objects.get(id=data.get('author'))
    data['editor'] = current_user.id
    if data.get('uid'):
        article = Article.objects.get(uid=data['uid'], status='draft')
        for field, value in data.items():
            setattr(article, field, value)
    else:
        article = Article(**data)
    if data.get('delete-image'):
        article.delete_image()
    if image:
        article.attach_image(image)
    article.save()
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('article_edit', uid=article.uid))
    else:
        return redirect(url_for('article.article_detail',
                                article_id=article.id,
                                slug=article.slug))


@article.route('/<slug>-<regex("\w{24}"):article_id>/')
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


@article.route('/<slug>-<regex("\w{24}"):article_id>/form/')
@login_required
@editor_required
def article_detail_form(slug, article_id):
    try:
        article = Article.objects.get(id=article_id, status='published')
    except Article.DoesNotExist:
        abort(HTTPStatus.NOT_FOUND, 'No article matches this id.')
    if article.slug != slug:
        return redirect(
            url_for('.article_detail_form', article_id=article.id,
                    slug=article.slug),
            code=HTTPStatus.MOVED_PERMANENTLY)
    return render_template('articles/edit.html', article=article)


@article.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def article_delete(article_id):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        abort(HTTPStatus.NOT_FOUND, 'No article found with this id.')
    article.delete()
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))
