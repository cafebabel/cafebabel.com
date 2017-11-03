from http import HTTPStatus

import mongoengine
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, fresh_login_required, login_required
from flask_mail import Message

from .. import app, mail
from ..core.helpers import editor_required
from ..users.models import User
from .models import Article


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


@app.route('/article/draft/<uid>/')
def article_edit(uid):
    try:
        article = Article.objects.get(uid=uid)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this uid.')
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@app.route('/article/new/')
@login_required
def article_new():
    if not current_user.has_role('editor'):
        flash("You don't have permission to access this ressource.", 'error')
        return redirect(url_for('home'))
    article = Article()
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


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
        return redirect(url_for('article_detail', article=article))


@app.route('/article/<article(status="published"):article>/')
def article_detail(article):
    if article.slug != article.url_slug:
        return redirect(
            url_for('article_detail', article=article),
            code=HTTPStatus.MOVED_PERMANENTLY)
    return render_template('articles/detail.html', article=article)


@app.route('/article/<id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def article_delete(id):
    try:
        Article.objects.get(id=id).delete()
    except (Article.DoesNotExist, mongoengine.errors.ValidationError):
        abort(HTTPStatus.NOT_FOUND, 'No article found with this id.')
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))
