from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .storage import CloudinaryMediaStorage


class CloudinaryMediaStorageTests(SimpleTestCase):
    def setUp(self):
        self.storage = CloudinaryMediaStorage()

    @patch('stackit.storage.cloudinary.uploader.upload')
    def test_save_uploads_image_and_returns_public_id(self, upload):
        upload.return_value = {
            'public_id': 'stackit/avatars/profile-photo-abc123',
        }
        image = SimpleUploadedFile(
            'Profile Photo.png',
            b'fake-image-content',
            content_type='image/png',
        )

        saved_name = self.storage.save('avatars/Profile Photo.png', image)

        self.assertEqual(
            saved_name,
            'stackit/avatars/profile-photo-abc123',
        )
        options = upload.call_args.kwargs
        self.assertTrue(options['public_id'].startswith(
            'stackit/avatars/profile-photo-'
        ))
        self.assertEqual(options['resource_type'], 'image')
        self.assertFalse(options['overwrite'])

    @patch('stackit.storage.cloudinary_url')
    def test_url_returns_secure_cloudinary_url(self, build_url):
        build_url.return_value = (
            'https://res.cloudinary.com/demo/image/upload/profile',
            {},
        )

        url = self.storage.url('stackit/avatars/profile')

        self.assertEqual(
            url,
            'https://res.cloudinary.com/demo/image/upload/profile',
        )
        build_url.assert_called_once_with(
            'stackit/avatars/profile',
            resource_type='image',
            secure=True,
        )

    @patch('stackit.storage.cloudinary.uploader.destroy')
    def test_delete_removes_cloudinary_asset(self, destroy):
        self.storage.delete('stackit/question_images/example')

        destroy.assert_called_once_with(
            'stackit/question_images/example',
            resource_type='image',
            invalidate=True,
        )
