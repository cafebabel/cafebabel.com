from flask import (Blueprint, current_app, redirect, render_template, request,
                   send_from_directory, url_for)

cores = Blueprint('cores', __name__)


@cores.route('/')
def home():
    lang = (request.accept_languages.best or '')[:2]
    if lang not in dict(current_app.config['LANGUAGES']):
        lang = current_app.config['DEFAULT_LANGUAGE']
    return redirect(url_for('.home_lang', lang=lang))


@cores.route('/<lang:lang>/')
def home_lang():
    return render_template('home.html')


@cores.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(current_app.config['UPLOADS_FOLDER'], filename)
