"""Auditable demo payments; prices and verification state belong to the server."""

import uuid

from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETE = "Complete", "Complete"
        FAILED = "Failed", "Failed"
        CANCELED = "Canceled", "Canceled"

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    course = models.ForeignKey("courses.Course", on_delete=models.PROTECT)
    transaction_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    provider_reference = models.CharField(max_length=100, blank=True)
    amount_npr = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    failed_code_attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(status="Complete") | models.Q(verified_at__isnull=False),
                name="completed_payment_verified",
            ),
            models.CheckConstraint(
                condition=models.Q(amount_npr__gt=0), name="payment_positive_amount"
            ),
        ]
