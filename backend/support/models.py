"""Public help content and incoming contact messages."""

from django.conf import settings
from django.db import models


class FAQ(models.Model):
    class Audience(models.TextChoices):
        ALL = "All", "All"
        LEARNER = "Learner", "Learners"
        TEACHER = "Teacher", "Lecturers"

    question = models.CharField(max_length=200)
    answer = models.TextField(max_length=2000)
    audience = models.CharField(max_length=7, choices=Audience.choices, default=Audience.ALL)
    sort_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sort_order", "id"]


class ContactMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
