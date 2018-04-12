from http import HTTPStatus
from io import BytesIO
from pathlib import Path

from flask.helpers import get_flashed_messages

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


def test_unauthenticated_user_cannot_access_login_required_page(client, user):
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.FOUND


def test_authenticated_user_can_access_login_required_page(client, user):
    login(client, user.email, 'password')
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK
    assert "<h1>Anonymous's profile</h1>" in response


def test_authenticated_user_can_access_his_email(client, user):
    login(client, user.email, 'password')
    response = client.get(f'/en/profile/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert user.email in response


def test_authenticated_user_cannot_access_others_email(client, user, user2):
    login(client, user2.email, 'password')
    response = client.get(f'/en/profile/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert user.email not in response


def test_editor_can_access_user_email(client, user, editor):
    login(client, editor.email, 'password')
    response = client.get(f'/en/profile/{user.id}/')
    assert response.status_code == HTTPStatus.OK
    assert user.email in response


def test_visitor_cannot_edit_user_profile(client, user):
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.FOUND
    assert ('/en/login?next=%2Fen%2Fprofile%2F'
            in response.headers.get('Location'))


def test_editor_can_edit_user_profile(client, user, editor):
    login(client, editor.email, 'password')
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.OK


def test_logout_user_cannot_access_login_required_page(client, user):
    login(client, user.email, 'password')
    logout(client)
    response = client.get(f'/en/profile/{user.id}/edit/')
    assert response.status_code == HTTPStatus.FOUND


def test_profile_image_should_save_and_render(app, client, user):
    login(client, user.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image = BytesIO(content.read())
    data = {'image': (image, 'image-name.jpg')}
    response = client.post(f'/en/profile/{user.id}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == ['Your profile has been updated :-)']
    user.reload()
    assert user.profile.image_filename == '/users/image-name.jpg'
    assert Path(app.config.get('UPLOADS_FOLDER') /
                'users' / 'image-name.jpg').exists()
    assert '<div style="background-image:url(/resized-images/' in response


def test_profile_image_unallowed_extension(app, client, user):
    login(client, user.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image = BytesIO(content.read())
    data = {'image': (image, 'image-name.zip')}
    assert 'zip' not in app.config.get('ALLOWED_EXTENSIONS')
    response = client.post(f'/en/profile/{user.id}/edit/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert get_flashed_messages() == [
        'There was an error in your profile submission: Unallowed extension.'
    ]
    user.reload()
    assert user.profile.image_filename is None
    assert not Path(app.config.get('UPLOADS_FOLDER') /
                    'users' / 'image-name.zip').exists()


def test_profile_big_image_should_raise(app, client, user):
    login(client, user.email, 'password')
    with open(Path(__file__).parent / 'big-image.jpeg', 'rb') as content:
        image = BytesIO(content.read())
    data = {'image': (image, 'image-name.jpg')}
    response = client.post(f'/en/profile/{user.id}/edit/', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    user.reload()
    assert not user.profile.image_filename


def test_login_complete_is_redirecting_to_appropriate_language(client, user):
    login(client, user.email, 'password')
    response = client.get('/login_complete/')
    assert response.status_code == HTTPStatus.FOUND
    assert (response.headers.get('Location') ==
            f'http://localhost/en/profile/{user.id}/')


def test_login_complete_redirects_if_not_logged_in(client, user):
    response = client.get('/login_complete/')
    assert response.status_code == HTTPStatus.FOUND
    assert ('/en/login?next=%2Flogin_complete%2F'
            in response.headers.get('Location'))


def test_user_suggest_basics(client, user):
    user.modify(profile__name='John Doe')
    response = client.get('/en/profile/suggest/?terms=john')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'name': 'John Doe',
        'id': str(user.id)
    }]


def test_user_suggest_many(client, editor, user, user2):
    response = client.get('/en/profile/suggest/?terms=anon')
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{
        'id': str(editor.id),
        'name': 'Anonymous'
    }, {
        'id': str(user.id),
        'name': 'Anonymous'
    }, {
        'id': str(user2.id),
        'name': 'Anonymous'
    }]


def test_user_suggest_too_short(client, tag):
    response = client.get('/en/profile/suggest/?terms=wo')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Suggestions are made available from 3-chars and more.' in response
