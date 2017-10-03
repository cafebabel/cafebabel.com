import datetime

from peewee import Model, CharField, DateField

from core import db


class User(Model):
    email = CharField(unique=True)
    firstname = CharField()
    lastname = CharField()
    creation_date = DateField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

    def to_dict(self):
        return self._data

    class Meta:
        database = db
