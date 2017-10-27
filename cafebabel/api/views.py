from flask import request, jsonify
from flask_login import current_user, login_required

from .. import app
from ..users.models import User, UserProfile, Role, UserRoles
from ..users import user_datastore


@app.route('/api/user/', methods=['post'])
def api_user_post():
    data = request.get_json()
    user = User.create(**data)
    return jsonify(user.to_dict()), 201


@app.route('/api/user/', methods=['put'])
@login_required
def api_user_put():
    data = request.get_json()
    profile_data = {k: data[k]
                    for k in ['name', 'socials', 'website', 'about']}
    (UserProfile.update(**profile_data)
                .where(UserProfile.user_id == current_user.id).execute())

    user = User.get(id=current_user.id)
    editor = Role.get(name='editor')
    if data.get('is_editor'):
        user_datastore.add_role_to_user(user=user, role=editor)
    else:
        user_datastore.remove_role_from_user(user=user, role=editor)
    return jsonify(user.to_dict())


@app.route('/api/user/<int:id>/', methods=['delete'])
@login_required
def api_user_delete(id):
    User.get(id=current_user.id).delete().execute()
    return '', 204
