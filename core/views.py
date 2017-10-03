from flask import abort, render_template, redirect, request, url_for

from . import app
from .models import User


@app.route('/')
def home():
    return '''
        <h1>Cafebabel</h1>
        <p>
            <a href=/user/>Create a profile</a>
        </p>
    '''


@app.route('/user/<int:id>/')
def user(id):
    try:
        user = User.get(id=id)
    except User.DoesNotExist:
        abort(404, 'User not found.')
    return render_template('user.html', user=user)


@app.route('/user/')
def user_new():
    return render_template('user_form.html', user=User())


@app.route('/user/<int:id>/edit/')
def user_edit(id):
    try:
        user = User.get(id=id)
    except User.DoesNotExist:
        abort(404, 'User not found.')
    return render_template('user_form.html', user=user)


@app.route('/user/save/', methods=['post'])
@app.route('/user/<int:id>/save/', methods=['post'])
def user_save(id=None):
    data = dict(request.form.items())
    if id:
        User.update(**data).where(User.id == id).execute()
        user = User.get(id=id)
    else:
        user = User.create(**data)
    return redirect(url_for('user', id=user.id))


@app.route('/user/<int:id>/delete/', methods=['post'])
def user_delete(id):
    try:
        User.delete().where(id == id).execute()
    except User.DoesNotExist:
        abort(404, 'User not found.')
    return redirect(url_for('home'))
