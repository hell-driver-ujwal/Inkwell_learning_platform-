"""Scenario graph with explicit endings and directional choices."""

from django.db import models


class Step(models.Model):
    class Outcome(models.TextChoices):
        BEST = "Best", "Best"
        ACCEPTABLE = "Acceptable", "Acceptable"
        POOR = "Poor", "Poor"

    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, related_name="steps"
    )
    text = models.CharField(max_length=1000)
    image = models.FileField(upload_to="scenarios/", blank=True)
    image_alt = models.CharField(max_length=150, blank=True)
    is_ending = models.BooleanField(default=False)
    outcome = models.CharField(max_length=10, choices=Outcome.choices, blank=True)
    feedback = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["id"]


class Choice(models.Model):
    from_step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name="choices")
    next_step = models.ForeignKey(Step, on_delete=models.PROTECT, related_name="incoming_choices")
    text = models.CharField(max_length=150)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_step=models.F("next_step")), name="no_direct_scenario_loop"
            )
        ]
