"""Reusable role checks, including forced password changes."""

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from accounts.models import AccountStatus, UserRole


class SessionReady(BasePermission):
    message = "Change your temporary password before continuing."

    def has_permission(self, request, view):
        user = request.user
        return not user.is_authenticated or (
            user.status == AccountStatus.ACTIVE and not user.must_change_password
        )


class IsLearner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.LEARNER


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            UserRole.TEACHER,
            UserRole.ADMIN,
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


def require_administrator(user):
    """Protect administrative service calls even outside an HTTP view."""
    if not (
        user.is_authenticated
        and user.is_active
        and user.role == UserRole.ADMIN
        and user.status == AccountStatus.ACTIVE
        and not user.must_change_password
    ):
        raise PermissionDenied("An active administrator is required.")
