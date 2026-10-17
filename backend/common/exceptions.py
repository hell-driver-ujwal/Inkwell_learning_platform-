"""Give API errors a predictable envelope without hiding unexpected exceptions."""

from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    if isinstance(exc, ProtectedError):
        exc = ValidationError("This record is referenced by learning history or other content.")
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"errors": response.data}
    return response
