from flask import render_template, request, flash, redirect, url_for, abort
from flask_mail import Message
from flask_login import current_user, login_required

from .. import app, mail
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
def article_draft(uid):
    try:
        article = Article.objects.get(uid=uid)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this uid.')
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@app.route('/article/<slug>-<id>/')
def article_read(id, slug):
    try:
        article = Article.objects.get(id=id, status='published')
    except Article.DoesNotExist:
        abort(404, 'No published article matches that id.')
    if article.slug != slug:
        return redirect(url_for(
            'article_read', slug=article.slug, id=article.id), code=301)
    return render_template('articles/read.html', article=article)


@app.route('/article/write/')
@login_required
def article_write():
    article = Article()
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@app.route('/article/create/', methods=['post'])
@login_required
def article_post():
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
        return redirect(url_for('article_draft', uid=article.uid))
    else:
        return redirect(url_for('article_read', slug=article.slug,
                                id=article.id))
