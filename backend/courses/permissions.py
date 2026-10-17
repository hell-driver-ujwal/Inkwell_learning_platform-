"""One source for ownership, publication, enrollment and preview access."""

from accounts.models import AccountStatus, UserRole
from common.models import PublicationStatus
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


def active_user(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.status == AccountStatus.ACTIVE
        and not user.must_change_password
    )


def owns_course(user, course):
    return (
        active_user(user)
        and user.role in (UserRole.TEACHER, UserRole.ADMIN)
        and course.teacher_id == user.id
    )


def can_preview(user, course):
    return active_user(user) and (user.role == UserRole.ADMIN or owns_course(user, course))


def is_enrolled(user, course):
    return (
        active_user(user)
        and user.role == UserRole.LEARNER
        and course.enrollments.filter(learner=user).exists()
    )


def can_study(user, course):
    return course.status == PublicationStatus.PUBLISHED and is_enrolled(user, course)


def require_owner(user, course):
    if not owns_course(user, course):
        raise PermissionDenied("Only the course author can change this content.")


def require_study(user, course):
    if not can_study(user, course):
        raise PermissionDenied("Enroll in this published course to continue.")


def can_read_material(user, material):
    if can_preview(user, material.course):
        return True
    published = (
        material.status == PublicationStatus.PUBLISHED
        and material.course.status == PublicationStatus.PUBLISHED
    )
    return published and (material.is_preview or can_study(user, material.course))


class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        course = obj if hasattr(obj, "teacher_id") else obj.course
        return owns_course(request.user, course)
