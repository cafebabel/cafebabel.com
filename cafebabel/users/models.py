import datetime

from flask import url_for
from flask_security import RoleMixin, UserMixin
from flask_login import current_user
from mongoengine import signals

from ..core.helpers import current_language
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
    old_pk = db.IntField()  # In use for migrations (references in articles).

    def __str__(self):
        return self.name or 'Anonymous'

    def get_id(self):
        return self._instance.id

    @property
    def upload_subpath(self):
        return 'users'


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255, unique=True)
    password = db.StringField(max_length=255)
    creation_date = db.DateTimeField(default=datetime.datetime.utcnow)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role, reverse_delete_rule=db.PULL),
                         default=[])
    profile = db.EmbeddedDocumentField(UserProfile)

    meta = {
        'indexes': ['profile.old_pk']
    }

    def __str__(self):
        return str(self.profile)

    @property
    def detail_url(self):
        return url_for('users.detail', id=self.id, lang=current_language())

    def is_me(self):
        return hasattr(current_user, 'id') and self.id == current_user.id

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
