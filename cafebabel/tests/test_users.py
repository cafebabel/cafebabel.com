from flask_security.confirmable import confirm_user

from ..users.models import  Role, UserRoles


def test_user_has_role(user):
    assert not user.has_role('editor')
    editor = Role.get(name='editor')
    UserRoles.create(user=user, role=editor)
    assert user.has_role('editor')


def test_admin_has_all_roles(admin):
    assert admin.has_role('anything')
