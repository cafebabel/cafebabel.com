import os

from flask import current_app, url_for
from werkzeug.utils import secure_filename

from .. import db


class UploadableImageMixin:
    image_filename = db.StringField()
    _upload_image = None

    @property
    def has_image(self):
        return bool(self.image_filename)

    @property
    def upload_subpath(self):
        raise NotImplemented()

    @property
    def image_url(self):
        if self.has_image:
            media_url = current_app.config.get('MEDIA_URL')
            if media_url:
                return f'{media_url}{self.image_filename}'
            return url_for('cores.uploads', filename=self.image_filename[1:])

    @property
    def image_path(self):
        if not self.has_image:
            return
        return str(current_app.config['UPLOADS_FOLDER']) + self.image_filename

    def attach_image(self, image):
        self._upload_image = image

    def delete_image(self):
        if not self.has_image:
            return
        self.image_path.unlink()
        self.image_filename = None
        self.save()

    @classmethod
    def store_image(cls, sender, document, **kwargs):
        if document is not None and document._upload_image:
            image_filename = secure_filename(document._upload_image.filename)
            document.image_filename = (f'/{document.upload_subpath}'
                                       f'/{image_filename}')
            folder = (current_app.config['UPLOADS_FOLDER'] /
                      document.upload_subpath)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            document._upload_image.save(str(folder / image_filename))
            document._upload_image = None
            document.save()

    @classmethod
    def delete_image_file(cls, sender, document, **kwargs):
        document.delete_image()
