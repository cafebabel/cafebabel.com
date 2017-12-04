from flask import Blueprint, current_app, request, jsonify
from flask_login import current_user, login_required

from ..users.models import User, UserProfile, Role

apis = Blueprint('apis', __name__)


@apis.route('/user/', methods=['put'])
@login_required
def user_put():
    user = User.objects.get(id=current_user.id)
    data = request.get_json()
    profile_data = {k: data[k]
                    for k in ['name', 'socials', 'website', 'about']}
    current_user.profile = UserProfile(**profile_data)
    current_user.save()
    editor = Role.objects.get(name='editor')
    if data.get('is_editor'):
        current_app.user_datastore.add_role_to_user(user=user, role=editor)
    else:
        current_app.user_datastore.remove_role_from_user(
            user=user, role=editor)
    return jsonify(user.to_dict())


@apis.route('/user/<id>/', methods=['delete'])
@login_required
def user_delete(id):
    User.objects.get(id=current_user.id).delete()
    return '', 204
