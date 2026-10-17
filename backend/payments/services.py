"""Local eSewa simulation only: no real payment provider or money transfer."""

import uuid

from common.models import PublicationStatus
from courses.models import Course
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from learning.models import Enrollment
from rest_framework.exceptions import ValidationError

from payments.models import Payment


@transaction.atomic
def begin_payment(*, learner, course_id):
    """Snapshot the course price on the server; never accept an amount from React."""
    course = get_object_or_404(Course.objects.select_for_update(), pk=course_id)
    if course.status != PublicationStatus.PUBLISHED or not course.is_paid:
        raise ValidationError("This course is not available for purchase.")
    if (
        Enrollment.objects.filter(learner=learner, course=course).exists()
        or Payment.objects.filter(
            learner=learner,
            course=course,
            status=Payment.Status.COMPLETE,
            verified_at__isnull=False,
        ).exists()
    ):
        raise ValidationError(
            "Already purchased. Enroll from the course page without paying again."
        )
    return Payment.objects.create(learner=learner, course=course, amount_npr=course.price_npr)


def complete_payment(*, learner, payment_id, phone, code):
    """Commit failed-code counters, and atomically verify payment plus enrollment."""
    error = None
    with transaction.atomic():
        candidate = get_object_or_404(Payment, pk=payment_id, learner=learner)
        course = Course.objects.select_for_update().get(pk=candidate.course_id)
        payment = Payment.objects.select_for_update().get(pk=payment_id, learner=learner)
        if payment.status == Payment.Status.COMPLETE:
            return payment
        if payment.status != Payment.Status.PENDING:
            raise ValidationError("This payment failed or was canceled. Start a new payment.")
        if course.status != PublicationStatus.PUBLISHED:
            raise ValidationError("This course is no longer available. No payment was made.")
        if code != phone[-4:]:
            payment.failed_code_attempts += 1
            if payment.failed_code_attempts >= 3:
                payment.status = Payment.Status.FAILED
            payment.save(update_fields=["failed_code_attempts", "status"])
            error = "Incorrect verification code. Three wrong codes fail the payment."
        else:
            payment.status = Payment.Status.COMPLETE
            payment.verified_at = timezone.now()
            payment.provider_reference = (
                f"ESW-{uuid.uuid4().hex[:8].upper()} ({phone[:2]}XXXXXX{phone[-2:]})"
            )
            payment.save(update_fields=["status", "verified_at", "provider_reference"])
            Enrollment.objects.get_or_create(learner=learner, course=course)
    if error:
        raise ValidationError(error)
    return payment


def cancel_payment(*, learner, payment_id):
    """A completed receipt is immutable, including on a late Cancel request."""
    payment = get_object_or_404(Payment, pk=payment_id, learner=learner)
    Payment.objects.filter(pk=payment.pk, status=Payment.Status.PENDING).update(
        status=Payment.Status.CANCELED
    )
