"""Invalidate access immediately when an account is deactivated."""

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import AccountStatus


class ActiveSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result and result[0].status != AccountStatus.ACTIVE:
            raise AuthenticationFailed("This account is not active.")
        return result
