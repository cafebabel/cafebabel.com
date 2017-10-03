import datetime

from flask_login import UserMixin
from peewee import CharField, DateField, Model
from playhouse.fields import PasswordField

from . import db


class User(Model, UserMixin):
    email = CharField(unique=True)
    firstname = CharField()
    lastname = CharField()
    password = PasswordField()
    creation_date = DateField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

    def to_dict(self):
        user_dict = self._data.copy()
        del user_dict['password']
        return user_dict

    class Meta:
        database = db
