from .. import db


class UploadableImageMixin:
    has_image = db.BooleanField(default=False)
    _upload_image = None

    def get_id(self):
        return self.id

    def get_images_url(self):
        raise NotImplemented()

    def get_images_path(self):
        raise NotImplemented()

    @property
    def image_url(self):
        if self.has_image:
            return f'{self.get_images_url()}/{self.get_id()}'

    @property
    def image_path(self):
        if not self.get_id():
            return
        return self.get_images_path() / str(self.get_id())

    def attach_image(self, image):
        self._upload_image = image

    def delete_image(self):
        if not self.has_image:
            return
        self.image_path.unlink()
        self.has_image = False
        self.save()

    @classmethod
    def store_image(cls, sender, document, **kwargs):
        if document._upload_image:
            document.has_image = True
            document._upload_image.save(str(document.image_path))
            document._upload_image = None
            document.save()

    @classmethod
    def delete_image_file(cls, sender, document, **kwargs):
        document.delete_image()
