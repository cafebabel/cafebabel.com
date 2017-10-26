import datetime

from flask_security import PeeweeUserDatastore, RoleMixin, Security, UserMixin
from peewee import (BooleanField, CharField, DateField, DateTimeField,
                    ForeignKeyField, TextField)
from playhouse.fields import PickledField
from playhouse.signals import post_save

from .. import app, db


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
        return str(self.profile)

    def to_dict(self):
        user_dict = self._data.copy()
        del user_dict['password']
        return user_dict

    @property
    def profile(self):
        return self.profiles.get()


@post_save(sender=User)
def create_user_profile(ModelClass, instance, created):
    UserProfile.create(user=instance)


class UserRoles(db.Model):
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)


class UserProfile(db.Model):
    name = CharField(null=True)
    user = ForeignKeyField(User, related_name='profiles', on_delete='CASCADE')
    socials = PickledField(null=True)
    website = CharField(null=True)
    about = CharField(null=True)

    def __str__(self):
        return self.name or str(self.user.email)


user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)
security = Security(app, user_datastore)
