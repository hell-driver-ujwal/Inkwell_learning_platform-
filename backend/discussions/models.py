"""Discussion posts with a single level of replies."""

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models


class Post(models.Model):
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.PROTECT, related_name="posts"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.CharField(max_length=2000, validators=[MinLengthValidator(2)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]
