"""Enrollment and completion actions preserve history when a learner leaves."""

from accounts.models import UserRole
from common.models import PublicationStatus
from courses.models import Course
from courses.permissions import active_user, require_study
from django.db import transaction
from payments.models import Payment
from rest_framework.exceptions import PermissionDenied, ValidationError

from learning.models import Completion, Enrollment


@transaction.atomic
def enroll_learner(*, learner, course):
    """Serialize enrollment against payment completion and course edits."""
    course = Course.objects.select_for_update().get(pk=course.pk)
    if not active_user(learner) or learner.role != UserRole.LEARNER:
        raise PermissionDenied("An active learner account is required.")
    if course.status != PublicationStatus.PUBLISHED:
        raise ValidationError("This course is not published.")
    existing = Enrollment.objects.filter(learner=learner, course=course).first()
    if existing:
        return existing
    paid = Payment.objects.filter(
        learner=learner, course=course, status=Payment.Status.COMPLETE, verified_at__isnull=False
    ).exists()
    if course.is_paid and not paid:
        raise PermissionDenied("Complete a verified demo payment before enrolling.")
    enrollment, _ = Enrollment.objects.get_or_create(learner=learner, course=course)
    return enrollment


def leave_course(*, learner, course):
    """Delete only enrollment; attempts, completions and receipts remain available."""
    Enrollment.objects.filter(learner=learner, course=course).delete()


def complete_material(*, learner, material):
    """Preview access alone never grants credit toward a certificate."""
    require_study(learner, material.course)
    if material.status != PublicationStatus.PUBLISHED:
        raise PermissionDenied("Draft lessons cannot be completed.")
    completion, _ = Completion.objects.get_or_create(learner=learner, material=material)
    return completion
