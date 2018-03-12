from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_mail import Message

from ... import mail
from ...core.helpers import current_language, obfuscate_email

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
    if request.method == 'POST':
        data = request.form
        msg = Message(
            f'Article proposal: {data["topic"]}',
            sender=data['email'],
            recipients=[
                current_app.config['EDITOR_EMAILS'][data.get('language', 'en')]
            ],
            body=BODY_EMAIL_TEMPLATE.format(**data.to_dict())
        )
        mail.send(msg)
        flash('Your proposal was successfully sent.', 'success')
        return redirect(url_for('cores.home_lang', lang=current_language()))

    editor_emails = {
        lang: obfuscate_email(email)
        for lang, email in current_app.config['EDITOR_EMAILS'].items()}

    return render_template(
        'articles/proposals/create.html',
        EDITORS_EMAIL_DEFAULT=current_app.config['EDITORS_EMAIL_DEFAULT'],
        editor_emails=editor_emails
    )
