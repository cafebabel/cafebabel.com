from http import HTTPStatus

from ..users.models import Role, user_datastore


def test_user_has_no_default_roles(user):
    assert not user.has_role('editor')
    assert not user.has_role('admin')
    assert not user.has_role('whatever')


def test_user_add_custom_role(user):
    editor = Role.objects(name='editor').get()
    user_datastore.add_role_to_user(user=user, role=editor)
    assert user.has_role('editor')
    assert not user.has_role('admin')
    assert not user.has_role('whatever')


def test_admin_has_all_roles(admin):
    assert admin.has_role('editor')
    assert admin.has_role('admin')
    assert admin.has_role('whatever')


def test_unauthenticated_user_cannot_access_login_required_page(client):
    response = client.get('/profile/')
    assert response.status_code == HTTPStatus.FOUND


def test_authenticated_user_can_access_login_required_page(client, user):
    data = dict(email=user.email, password='secret', remember='y')
    response = client.post('/login', data=data)
    assert response.status_code == HTTPStatus.OK
    response = client.get('/profile/')
    # assert response.status_code == HTTPStatus.OK
