from http import HTTPStatus
from io import BytesIO
from pathlib import Path

from ..users.models import Role
from .utils import login, logout


def test_user_has_no_default_roles(user):
    assert not user.has_role('editor')
    assert not user.has_role('whatever')


def test_user_add_custom_role(app, user):
    editor = Role.objects.get(name='editor')
    app.user_datastore.add_role_to_user(user=user, role=editor)
    assert user.has_role('editor')
    assert not user.has_role('whatever')


def test_unauthenticated_user_cannot_access_login_required_page(client):
    response = client.get('/profile/')
    assert response.status_code == HTTPStatus.FOUND


def test_authenticated_user_can_access_login_required_page(client, user):
    login(client, user.email, 'password')
    response = client.get('/profile/', follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b'<h1>user@example.com\'s profile</h1>' in response.data


def test_visitor_cannot_edit_user_profile(client, user):
    response = client.get(f'/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_editor_can_edit_user_profile(client, user, editor):
    login(client, editor.email, 'password')
    response = client.get(f'/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK


def test_logout_user_cannot_access_login_required_page(client, user):
    login(client, user.email, 'password')
    logout(client)
    response = client.get('/profile/')
    assert response.status_code == HTTPStatus.FOUND


def test_profile_image_should_save_and_render(app, client, user):
    login(client, user.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image = BytesIO(content.read())
    data = {'image': (image, 'image-name.jpg')}
    response = client.post(f'/profile/{user.id}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    user.reload()
    assert user.profile.has_image
    assert Path(app.config.get('USERS_IMAGES_PATH') / str(user.id)).exists()
    assert f'<img src={user.profile.image_url}' in response
