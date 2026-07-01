from pathlib import PurePosixPath
from uuid import uuid4
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify


@deconstructible
class CloudinaryMediaStorage(Storage):
    """Store user-uploaded images in Cloudinary using Django's storage API."""

    def _save(self, name, content):
        path = PurePosixPath(name)
        folder = (PurePosixPath('stackit') / path.parent).as_posix()
        stem = slugify(path.stem) or 'image'
        public_id = f'{folder}/{stem}-{uuid4().hex[:12]}'

        content.seek(0)
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            resource_type='image',
            overwrite=False,
        )
        return result['public_id']

    def delete(self, name):
        if name:
            cloudinary.uploader.destroy(
                name,
                resource_type='image',
                invalidate=True,
            )

    def exists(self, name):
        return False

    def url(self, name):
        return cloudinary_url(
            name,
            resource_type='image',
            secure=True,
        )[0]
