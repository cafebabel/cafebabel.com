from flask import abort, render_template, request

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


@app.route('/user/')
def user_new():
    return render_template('user.html', user=User(), edit=True)


@app.route('/user/<int:id>/')
def user(id):
    try:
        user = User.get(id=id)
    except User.DoesNotExist:
        abort(404, 'User not found.')
    return render_template('user.html', user=user,
                           edit=('edit' in request.args))
