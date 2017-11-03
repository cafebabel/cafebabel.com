import json
from http import HTTPStatus

import pytest

from ..users.models import User
from .utils import login


def test_update_profile(client, user):
    login(client, user.email, 'secret')
    data = {
        'name': 'name',
        'socials': {
            'twitter': 'twitter',
            'facebook': 'facebook',
            'medium': 'medium',
            'flickr': 'flickr',
            'pinterest': 'pinterest',
            'instagram': 'instagram',
        },
        'website': 'website',
        'about': 'about'
    }
    response = client.put(f'/api/user/',
                          data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == HTTPStatus.OK
    user = User.objects.get(id=user.id)
    assert user.profile.name == 'name'
    assert user.profile.socials['twitter'] == 'twitter'


def test_delete_profile(client, user):
    login(client, user.email, 'secret')
    response = client.delete(f'/api/user/{user.idstr}/')
    assert response.status_code == HTTPStatus.NO_CONTENT
    with pytest.raises(User.DoesNotExist):
        User.objects.get(id=user.id)
