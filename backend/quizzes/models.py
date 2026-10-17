"""Quiz questions, options and submitted answers."""

from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models


class Question(models.Model):
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, related_name="questions"
    )
    text = models.CharField(max_length=500, validators=[MinLengthValidator(5)])
    marks = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    sort_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sort_order", "id"]


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["question", "text"], name="unique_quiz_option")
        ]
        ordering = ["id"]


class Answer(models.Model):
    attempt = models.ForeignKey(
        "activities.Attempt", on_delete=models.CASCADE, related_name="quiz_answers"
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_option = models.ForeignKey(Option, null=True, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="one_answer_per_question")
        ]
