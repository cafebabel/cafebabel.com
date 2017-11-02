from flask import render_template, request, flash, redirect, url_for
from flask_mail import Message

from .. import app, mail


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


@app.route('/article/create/')
def article_create():
    article = Article()
    return render_template('articles/create.html', article=article)


@app.route('/article/create/', methods=['post'])
def article_post():
    article = Article.create(**request.form)
    return redirect(url_for('draft_read', id=article.id))


@app.route('/draft/<id>/')
def draft_read(id):
    article = Article.get(id=id, status='draft')
    return render_template('articles/read.html', article=article)
