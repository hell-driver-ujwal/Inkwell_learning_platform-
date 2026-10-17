"""Page analytics intentionally contain no user identifiers or IP addresses."""

from django.db import models


class PageView(models.Model):
    path = models.CharField(max_length=200)
    viewer_role = models.CharField(max_length=7)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["viewed_at", "id"]
        indexes = [models.Index(fields=["viewed_at", "path"])]
