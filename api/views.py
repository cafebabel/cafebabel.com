from flask import request, jsonify

from core import app
from core.models import User


@app.route('/api/user/', methods=['post'])
def api_user_post():
    data = request.get_json()
    try:
        User.get(email=data['email'])
        return (jsonify({'error': 'A user with this email already exists.'}),
                400)
    except User.DoesNotExist:
        pass
    user = User.create(**data)
    return jsonify(user.to_dict()), 201


@app.route('/api/user/<int:id>/', methods=['put'])
def api_user_put(id):
    try:
        user = User.get(id=id)
    except User.DoesNotExist:
        return {'error': 'User not found.'}, 404
    data = request.get_json()
    try:
        User.select().where(User.id != id, User.email == data['email']).get()
        return (jsonify({'error': 'A user with this email already exists.'}),
                400)
    except User.DoesNotExist:
        pass
    User.update(**request.get_json()).where(User.id == id).execute()
    user = User.get(id=id)
    return jsonify(user.to_dict())


@app.route('/api/user/<int:id>/', methods=['delete'])
def api_user_delete(id):
    User.get(id=id).delete().execute()
    return '', 204
