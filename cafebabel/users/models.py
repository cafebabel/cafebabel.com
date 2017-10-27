import datetime

from flask_security import RoleMixin, UserMixin
from peewee import (BooleanField, CharField, DateField, DateTimeField,
                    ForeignKeyField, TextField)
from playhouse.signals import post_save
from playhouse.fields import PickledField

from ..core import db


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

    def has_role(self, role, or_admin=True):
        if super(User, self).has_role('admin') and or_admin:
            return True
        return super(User, self).has_role(role)

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
