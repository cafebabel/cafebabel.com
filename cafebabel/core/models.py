import datetime

from flask_security import RoleMixin, UserMixin
from flask_security.signals import user_confirmed
from peewee import (BooleanField, CharField, DateField, DateTimeField,
                    ForeignKeyField, TextField)

from . import db


class Role(db.Model, RoleMixin):
    name = CharField(unique=True)
    description = TextField(null=True)


class User(db.Model, UserMixin):
    email = CharField(unique=True)
    password = TextField()
    creation_date = DateField(default=datetime.datetime.utcnow)
    active = BooleanField(default=True)
    confirmed_at = DateTimeField(null=True)

    def __str__(self):
        return self.email

    def to_dict(self):
        user_dict = self._data.copy()
        del user_dict['password']
        return user_dict


@user_confirmed.connect
def create_user_profile(app, user):
    UserProfile.create(user=user)


class UserRoles(db.Model):
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)


class UserProfile(db.Model):
    name = CharField(null=True)
    user = ForeignKeyField(User)

    def __str__(self):
        return self.name if self.name else str(self.user)
