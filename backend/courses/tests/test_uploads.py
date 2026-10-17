"""Upload and protected-media checks run without exposing a public media route."""

import tempfile
from pathlib import Path

from common.tests.factories import LearningTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.exceptions import ValidationError

from courses.uploads import validate_upload


class UploadTests(LearningTestCase):
    def test_fake_pdf_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_upload(SimpleUploadedFile("document.pdf", b"<script>alert(1)</script>"), "PDF")

    def test_script_extension_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_upload(SimpleUploadedFile("script.html", b"%PDF-1.7"), "PDF")

    def test_private_file_requires_enrollment(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            Path(directory, "private.pdf").write_bytes(b"%PDF-1.7\nTest PDF")
            self.material.kind = "PDF"
            self.material.file = "private.pdf"
            self.material.save()
            path = f"/api/materials/{self.material.id}/file/"
            self.assertEqual(self.client.get(path).status_code, 403)
            self.sign_in(self.learner)
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")
            response.close()
            self.assertEqual(self.client.get("/media/private.pdf").status_code, 404)

    def test_captions_use_the_same_access_check(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            Path(directory, "video.vtt").write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nHello")
            self.material.kind = "Video"
            self.material.file = "video.mp4"
            self.material.save()
            path = f"/api/materials/{self.material.id}/captions/"
            self.assertEqual(self.client.get(path).status_code, 403)
            self.sign_in(self.learner)
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_byte_ranges_allow_seeking_without_bypassing_authorization(self):
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            Path(directory, "audio.mp3").write_bytes(b"0123456789")
            self.material.kind = "Audio"
            self.material.file = "audio.mp3"
            self.material.save()
            path = f"/api/materials/{self.material.id}/file/"
            self.assertEqual(self.client.get(path, HTTP_RANGE="bytes=2-5").status_code, 403)
            self.sign_in(self.learner)
            response = self.client.get(path, HTTP_RANGE="bytes=2-5")
            self.assertEqual(response.status_code, 206)
            self.assertEqual(response["Content-Range"], "bytes 2-5/10")
            self.assertEqual(b"".join(response.streaming_content), b"2345")
            response = self.client.get(path, HTTP_RANGE="bytes=-3")
            self.assertEqual(b"".join(response.streaming_content), b"789")
            self.assertEqual(self.client.get(path, HTTP_RANGE="bytes=12-").status_code, 416)
