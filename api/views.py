from flask import request, jsonify

from core import app
from core.models import User


@app.route('/api/user/', methods=['post'])
def api_user_post():
    user = User.create(**request.get_json())
    return jsonify(user.to_dict())


@app.route('/api/user/<int:id>/', methods=['put'])
def api_user_put(id):
    User.update(**request.get_json()).where(User.id == id).execute()
    user = User.get(id=id)
    return jsonify(user.to_dict())
