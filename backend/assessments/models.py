"""Confidence statements and one-to-five learner ratings."""

from django.db import models


class Statement(models.Model):
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, related_name="statements"
    )
    text = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sort_order", "id"]


class Response(models.Model):
    attempt = models.ForeignKey(
        "activities.Attempt", on_delete=models.CASCADE, related_name="ratings"
    )
    statement = models.ForeignKey(Statement, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "statement"], name="one_rating_per_statement"
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5), name="rating_range"
            ),
        ]
