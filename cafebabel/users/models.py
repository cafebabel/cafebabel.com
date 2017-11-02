import datetime

from flask_security import (MongoEngineUserDatastore, RoleMixin, Security,
                            UserMixin)
from mongoengine import CASCADE, signals

from .. import app, db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    password = db.StringField(max_length=255)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

    def __str__(self):
        return str(self.profile)

    @property
    def idstr(self):
        # Otherwise returns an ObjectID, not good in url_for.
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.idstr,
            'email': self.email,
        }

    def has_role(self, role, or_admin=True):
        if super(User, self).has_role('admin') and or_admin:
            return True
        return super(User, self).has_role(role)

    @property
    def profile(self):
        return UserProfile.objects.get(user=self)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created', False):
            # Create the profile only on creation (vs. update).
            UserProfile.objects.create(user=document)


signals.post_save.connect(User.post_save, sender=User)


class UserProfile(db.Document):
    name = db.StringField()
    user = db.ReferenceField(User, reverse_delete_rule=CASCADE)
    socials = db.DictField()
    website = db.StringField()
    about = db.StringField()

    def __str__(self):
        return self.name or str(self.user.email)


user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)
