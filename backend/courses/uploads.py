"""Validate uploaded files and give them non-user-controlled storage names."""

import uuid
from pathlib import Path

from rest_framework.exceptions import ValidationError


def validate_upload(upload, kind, cover=False):
    """Apply the original type/size limits and verify common file signatures."""
    allowed = {
        "Image": ({".jpg", ".jpeg", ".png", ".gif"}, 2),
        "PDF": ({".pdf"}, 10),
        "Video": ({".mp4"}, 25),
        "Audio": ({".mp3"}, 10),
    }
    extensions, megabytes = allowed.get(kind, (set(), 0))
    extension = Path(upload.name).suffix.lower()
    if (
        extension not in extensions
        or (cover and extension == ".gif")
        or not 0 < upload.size <= megabytes * 1024 * 1024
    ):
        raise ValidationError("Use an image up to 2 MB, PDF/MP3 up to 10 MB, or MP4 up to 25 MB.")
    header = upload.read(32)
    upload.seek(0)
    valid = True
    if kind == "Image":
        from PIL import Image, UnidentifiedImageError

        try:
            picture = Image.open(upload)
            picture.verify()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ValidationError("This is not a valid image.") from exc
        finally:
            upload.seek(0)
    elif kind == "PDF":
        valid = header.startswith(b"%PDF-")
    elif kind == "Video":
        valid = b"ftyp" in header
    elif kind == "Audio":
        valid = header.startswith(b"ID3") or (
            len(header) >= 2 and header[0] == 255 and header[1] & 224 == 224
        )
    if not valid:
        raise ValidationError("File content does not match the selected format.")
    upload.name = f"{uuid.uuid4().hex}{extension}"
    return upload
