from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request)
from flask_mail import Message

from ... import mail
from ...core.helpers import current_language, lang_url_for, obfuscate_email

proposals = Blueprint('proposals', __name__)

BODY_EMAIL_TEMPLATE = '''
Language: {language}
Name: {name}
Email: {email}
City: {city}
Topic: {topic}
Angle: {angle}
Media: {media}
Format: {format}
Section: {section}
Addiction comment: {additional}
'''


@proposals.route('/new/', methods=['get', 'post'])
def create():
    editor_email = current_app.config['EDITOR_EMAILS'][current_language()]
    if request.method == 'POST':
        data = request.form.to_dict()
        data['language'] = current_language()
        msg = Message(
            f'Article proposal: {data["topic"]}',
            sender=data['email'],
            recipients=[editor_email],
            body=BODY_EMAIL_TEMPLATE.format(**data)
        )
        mail.send(msg)
        flash('Thanks! We’ll be getting back to you asap', 'success')
        return redirect(lang_url_for('cores.home_lang'))

    return render_template(
        'articles/proposals/create.html',
        editor_email=obfuscate_email(editor_email)
    )
