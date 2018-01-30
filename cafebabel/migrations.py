import json
from datetime import datetime, timezone

import click
from cafebabel.users.models import Role
from progressist import ProgressBar


def iterate_over_json_file(filename):
    with open(filename) as json_file:
        return json.loads(json_file.read())


def migrate_users(app, limit):
    click.echo('Starting users migration.')
    ds = app.user_datastore
    old_users = iterate_over_json_file('users.json')
    if limit:
        old_users = old_users[:limit]
    bar = ProgressBar(
        total=len(old_users),
        template=('{prefix} {animation} {percent} ({done}/{total}) '
                  'ETA: {eta:%H:%M}'),
        done_char='👤')
    editor_role = Role.objects.get(name='editor')
    with app.app_context():
        for old_user in bar.iter(old_users):
            data = old_user['fields']
            # TODO: deal properly with passwords import, see #192
            password = data['password']
            creation_date = datetime.strptime(data['date_joined'],
                                              '%Y-%m-%dT%H:%M:%S')
            creation_date.replace(tzinfo=timezone.utc)
            user = ds.create_user(email=data['email'],
                                  password=password,
                                  creation_date=creation_date)
            user.profile.name = f'{data["first_name"]} {data["last_name"]}'
            user.profile.old_pk = old_user['pk']
            user.save()
            if data['is_superuser'] or data['is_staff']:
                ds.add_role_to_user(user, editor_role)
    click.echo('Users migrated.')
