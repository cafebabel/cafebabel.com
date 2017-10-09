from flask import abort, render_template, request
from flask_login import login_required

from . import app
from .models import UserProfile


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/profile/')
def profile_new():
    return render_template('profile.html', profile=UserProfile(), edit=True)


@app.route('/profile/<int:id>/')
@login_required
def profile(id):
    try:
        profile = UserProfile.get(user_id=id)
    except UserProfile.DoesNotExist:
        abort(404, 'User not found.')
    return render_template('user.html', profile=profile,
                           edit=('edit' in request.args))
