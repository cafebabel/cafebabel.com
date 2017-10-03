from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from core import app
from .forms import LoginForm
from core.models import User
from .utils import is_safe_url


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        try:
            user = User.get(email=form.email.data)
        except User.UserDoesNotExist:
            error = 'Invalid email'  # TODO: security.
            return render_template('login.html', form=form, error=error)
        if not user.password.check_password(form.password.data):
            error = 'Invalid credentials'
            return render_template('login.html', form=form, error=error)
        login_user(user)
        flash('Logged in successfully.')
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('home'))

    return render_template('login.html', form=form, error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
