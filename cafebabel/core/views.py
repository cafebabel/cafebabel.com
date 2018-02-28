from flask import (Blueprint, abort, current_app, redirect, render_template,
                   request, send_from_directory, url_for)
from flask_login import current_user, login_required

from ..articles.models import Article

cores = Blueprint('cores', __name__)


def get_language():
    lang = (request.accept_languages.best or '')[:2]
    if lang not in dict(current_app.config['LANGUAGES']):
        lang = current_app.config['DEFAULT_LANGUAGE']
    return lang


@cores.route('/')
def home():
    return redirect(url_for('.home_lang', lang=get_language()))


@cores.route('/login_complete/')
@login_required
def profile_redirect():
    """In use to redirect after login complete.

    Flask-login does not allow us to redirect dynamically to the current
    language so we set that fake view to proper redirect.
    """
    return redirect(
        url_for('users.detail', lang=get_language(), id=current_user.id))


@cores.route('/<lang:lang>/')
def home_lang():
    articles = Article.objects.published()[:25]
    return render_template('home.html', articles=articles)


@cores.route('/<path:filename>')
def uploads(filename):
    """Fallback to local images available for dev only.

    Note: this route will only be called if `MEDIA_URL` is not set.
    """
    if current_app.config.get('DEBUG'):
        return send_from_directory(current_app.config['UPLOADS_FOLDER'],
                                   filename)
    abort(404)
