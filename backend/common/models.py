"""Small shared model vocabulary; domain workflows live in their own apps."""

from django.db import models


class PublicationStatus(models.TextChoices):
    DRAFT = "Draft", "Draft"
    PUBLISHED = "Published", "Published"
