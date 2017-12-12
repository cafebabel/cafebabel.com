import datetime

from flask import current_app
from flask_security import RoleMixin, UserMixin
from flask_login import current_user
from mongoengine import signals

from ..core.mixins import UploadableImageMixin
from .. import db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class UserProfile(db.EmbeddedDocument, UploadableImageMixin):
    name = db.StringField()
    socials = db.DictField()
    website = db.StringField()
    about = db.StringField()

    def __str__(self):
        return self.name or 'Anonymous'

    def get_id(self):
        return self._instance.id

    def get_images_url(self):
        return current_app.config.get('USERS_IMAGES_URL')

    def get_images_path(self):
        return current_app.config.get('USERS_IMAGES_PATH')


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

    def is_me(self):
        return self == current_user

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

    @classmethod
    def store_image(cls, sender, document, **kwargs):
        return UserProfile.store_image(sender=UserProfile,
                                       document=document.profile,
                                       **kwargs)

    @classmethod
    def delete_image_file(cls, sender, document, **kwargs):
        return UserProfile.delete_image_file(sender=UserProfile,
                                             document=document.profile,
                                             **kwargs)


signals.post_save.connect(User.post_save, sender=User)
signals.post_save.connect(User.store_image, sender=User)
signals.pre_delete.connect(User.delete_image_file, sender=User)
