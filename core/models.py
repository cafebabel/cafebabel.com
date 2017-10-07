import datetime

from flask_security import RoleMixin, UserMixin
from peewee import (BooleanField, CharField, DateField, DateTimeField,
                    ForeignKeyField, TextField)

from . import db


class Role(db.Model, RoleMixin):
    name = CharField(unique=True)
    description = TextField(null=True)


class User(db.Model, UserMixin):
    email = CharField(unique=True)
    firstname = CharField()
    lastname = CharField()
    password = TextField()
    creation_date = DateField(default=datetime.datetime.utcnow)
    active = BooleanField(default=True)
    confirmed_at = DateTimeField(null=True)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

    def to_dict(self):
        user_dict = self._data.copy()
        del user_dict['password']
        return user_dict


class UserRoles(db.Model):
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)
