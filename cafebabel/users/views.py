from flask import Blueprint, abort, render_template
from flask_login import login_required, current_user

from ..articles.models import Article
from .models import User


users = Blueprint('users', __name__)


@users.route('/')
@login_required
def profile():
    user = current_user
    articles = Article.objects.filter(author=user.id, status='published')
    return render_template('users/profile.html', user=user, edit=True,
                           articles=articles)


@users.route('/<id>/')
def profile_user(id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        abort(404, 'User not found.')
    articles = Article.objects.filter(author=user, status='published')
    return render_template('users/profile.html', user=user, articles=articles,
                           edit=False)
