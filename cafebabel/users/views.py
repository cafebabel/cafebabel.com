from flask import abort, render_template
from flask_login import login_required, current_user

from ..articles.models import Article
from .. import app
from .models import User


@app.route('/profile/')
@login_required
def profile():
    user = current_user
    articles = Article.objects.filter(author=user.id, status='published')
    return render_template('profile.html', user=user, edit=True, articles=articles)


@app.route('/profile/<id>/')
def profile_user(id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        abort(404, 'User not found.')
    articles = Article.objects.filter(author=user, status='published')
    return render_template('profile.html', user=user, articles=articles,
                           edit=False)
