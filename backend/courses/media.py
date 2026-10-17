"""Authorized private files, including byte ranges for video/audio seeking."""

import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse


def read_file_range(path, start, length):
    """Read only the requested bytes and close the file when streaming ends."""
    with path.open("rb") as media_file:
        media_file.seek(start)
        remaining = length
        while remaining:
            chunk = media_file.read(min(65536, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def parse_byte_range(header, size):
    """Return one inclusive range; reject malformed or unsatisfiable requests."""
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", header)
    if not match or size == 0:
        raise ValueError("Invalid byte range.")
    first, last = match.groups()
    if not first:
        suffix = int(last or 0)
        if suffix <= 0:
            raise ValueError("Invalid suffix range.")
        return max(0, size - suffix), size - 1
    start = int(first)
    end = min(int(last), size - 1) if last else size - 1
    if start > end:
        raise ValueError("Range is outside the file.")
    return start, end


def protected_file_response(field, request=None):
    """Authorize the object before calling; storage paths never become public URLs."""
    if not field:
        raise Http404("File not found.")
    path = Path(field.path).resolve()
    if not path.is_relative_to(Path(settings.MEDIA_ROOT).resolve()) or not path.is_file():
        raise Http404("File not found.")
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    size = path.stat().st_size
    range_header = request.headers.get("Range") if request is not None else None
    if range_header:
        try:
            start, end = parse_byte_range(range_header, size)
        except ValueError:
            response = HttpResponse(status=416)
            response["Content-Range"] = f"bytes */{size}"
        else:
            response = StreamingHttpResponse(
                read_file_range(path, start, end - start + 1),
                status=206,
                content_type=content_type,
            )
            response["Content-Range"] = f"bytes {start}-{end}/{size}"
            response["Content-Length"] = str(end - start + 1)
    else:
        response = FileResponse(path.open("rb"), content_type=content_type)
    response["Accept-Ranges"] = "bytes"
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    # PDF lessons are embedded by our own frontend, never by another origin.
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response


def caption_response(material):
    """Legacy captions are sidecars; authorize the material before calling this."""
    if not material.file:
        raise Http404("Captions not found.")
    path = Path(material.file.path).resolve().with_suffix(".vtt")
    if not path.is_relative_to(Path(settings.MEDIA_ROOT).resolve()) or not path.is_file():
        raise Http404("Captions not found.")
    response = HttpResponse(path.read_bytes(), content_type="text/vtt; charset=utf-8")
    response["Cache-Control"] = "private, no-store"
    return response
