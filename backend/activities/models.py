"""Shared curriculum metadata and durable play/attempt history."""

import uuid

from common.models import PublicationStatus
from django.conf import settings
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models


class Activity(models.Model):
    class Kind(models.TextChoices):
        QUIZ = "Quiz", "Quiz"
        ASSESSMENT = "SelfAssessment", "Self assessment"
        DISCUSSION = "Discussion", "Discussion"
        GAME = "Game", "Game"
        SCENARIO = "Scenario", "Scenario"

    topic = models.ForeignKey("courses.Topic", on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    description = models.TextField(max_length=1000, blank=True)
    kind = models.CharField(max_length=14, choices=Kind.choices)
    status = models.CharField(
        max_length=9, choices=PublicationStatus.choices, default=PublicationStatus.DRAFT
    )
    sort_order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    time_limit_minutes = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(180)])
    max_attempts = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(10)])
    game_template = models.CharField(max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)
    start_step = models.ForeignKey(
        "scenarios.Step",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="starting_activities",
    )
    revision = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]

    @property
    def course(self):
        return self.topic.course

    def __str__(self):
        return self.title


class Attempt(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT, related_name="attempts")
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="attempts"
    )
    ending_step = models.ForeignKey(
        "scenarios.Step", null=True, blank=True, on_delete=models.PROTECT
    )
    score_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(score_percent__isnull=True)
                | models.Q(score_percent__gte=0, score_percent__lte=100),
                name="attempt_score_range",
            )
        ]
        indexes = [models.Index(fields=["learner", "activity"])]


class PlaySession(models.Model):
    """Server-owned timer and branch state; previews never create Attempts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="runs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preview = models.BooleanField(default=False)
    revision = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)
    current_step = models.ForeignKey("scenarios.Step", null=True, on_delete=models.SET_NULL)
    step_version = models.PositiveIntegerField(default=0)
    result = models.JSONField(default=dict, blank=True)
    attempt = models.OneToOneField(Attempt, null=True, on_delete=models.SET_NULL)
