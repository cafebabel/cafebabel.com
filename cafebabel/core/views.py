from flask import abort, render_template
from flask_login import login_required, current_user

from .. import app
from .models import User


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/profile/')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user, edit=True)


@app.route('/profile/<int:id>/')
def profile_user(id):
    try:
        user = User.get(id=id)
    except User.DoesNotExist:
        abort(404, 'User not found.')
    return render_template('profile.html', user=user, edit=False)
