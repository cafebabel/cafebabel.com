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
def article_edit(uid):
    try:
        article = Article.objects.get(uid=uid)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this uid.')
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@app.route('/article/<slug>-<id>/')
def article_detail(id, slug):
    try:
        article = Article.objects.get(id=id, status='published')
    except Article.DoesNotExist:
        abort(404, 'No published article matches that id.')
    if article.slug != slug:
        return redirect(url_for(
            'article_detail', slug=article.slug, id=article.id), code=301)
    return render_template('articles/detail.html', article=article)


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
        return redirect(url_for('article_detail', slug=article.slug,
                                id=article.id))


@app.route('/article/<id>/delete/')
@login_required
def article_delete(id):
    try:
        Article.objects.get(id=id).delete()
    except Article.DoesNotExist:
        abort('No article found with this id.', 404)
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))
