from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_mail import Message

from ... import app, mail

proposals = Blueprint('proposals', __name__)

BODY_EMAIL_TEMPLATE = '''
Name: {data[name]}
City: {data[city]}
Angle: {data[angle]}
Format: {data[format]}
Additional infos: {data[additional]}
'''


@proposals.route('/new/', methods=['get', 'post'])
def create():
    if request.method == 'POST':
        data = request.form
        msg = Message(
            f'Article proposal: {data["topic"]}',
            sender=data['email'],
            recipients=[
                app.config['EDITOR_EMAILS'][data.get('language', 'en')]
            ],
            body=BODY_EMAIL_TEMPLATE.format(data=data)
        )
        mail.send(msg)
        flash('Your proposal was successfully sent.', 'success')
        return redirect(url_for('home'))

    return render_template('articles/proposals/create.html')
