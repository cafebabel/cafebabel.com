import datetime

from flask_security import RoleMixin, UserMixin
from mongoengine import signals

from .. import db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class UserProfile(db.EmbeddedDocument):
    name = db.StringField()
    socials = db.DictField()
    website = db.StringField()
    about = db.StringField()

    def __str__(self):
        return self.name


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    password = db.StringField(max_length=255)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role, reverse_delete_rule=db.PULL),
                         default=[])
    profile = db.EmbeddedDocumentField(UserProfile)

    def __str__(self):
        return str(self.profile)

    @property
    def idstr(self):
        # Otherwise returns an ObjectID, not good in url_for.
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.idstr,
        }

    def has_role(self, role, or_admin=True):
        if super(User, self).has_role('admin') and or_admin:
            return True
        return super(User, self).has_role(role)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created', False):
            # Create the profile only on creation (vs. update).
            document.profile = UserProfile(name=document.email)
            document.save()


signals.post_save.connect(User.post_save, sender=User)
