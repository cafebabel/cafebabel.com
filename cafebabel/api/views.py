from flask import request, jsonify
from flask_login import current_user, login_required

from .. import app
from ..users.models import User, UserProfile


@app.route('/api/user/', methods=['post'])
def api_user_post():
    data = request.get_json()
    user = User.create(**data)
    return jsonify(user.to_dict()), 201


@app.route('/api/user/', methods=['put'])
@login_required
def api_user_put():
    id = current_user.id
    (UserProfile.update(**request.get_json())
                .where(UserProfile.user_id == id).execute())
    user = User.get(id=id)
    return jsonify(user.to_dict())


@app.route('/api/user/<int:id>/', methods=['delete'])
@login_required
def api_user_delete(id):
    User.get(id=current_user.id).delete().execute()
    return '', 204
