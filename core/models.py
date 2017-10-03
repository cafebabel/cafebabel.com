import datetime
import os
import uuid

from flask_login import UserMixin
from peewee import CharField, DateField, Model
from playhouse.fields import PasswordField

from . import db


class User(Model, UserMixin):
    email = CharField(unique=True)
    firstname = CharField()
    lastname = CharField()
    password = PasswordField()
    session_token = CharField()
    creation_date = DateField(default=datetime.datetime.utcnow)

    class Meta:
        database = db

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

    def save(self, *args, **kwargs):
        if not self.session_token:
            self.session_token = uuid.UUID(bytes=os.urandom(16))
        super().save(*args, **kwargs)

    def to_dict(self):
        user_dict = self._data.copy()
        del user_dict['password']
        return user_dict

    def get_id(self):
        """In use by flask_login to retrieve the user from session.

        See https://flask-login.readthedocs.io/en/latest/#alternative-tokens
        for reasons why.
        """
        return self.session_token
