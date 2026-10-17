"""Course catalogue and ordered lesson content owned by an author."""

from common.models import PublicationStatus
from django.conf import settings
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(2)])
    description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="authored_courses"
    )
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="courses")
    title = models.CharField(max_length=100, validators=[MinLengthValidator(5)])
    description = models.TextField(max_length=1000, validators=[MinLengthValidator(20)])
    cover = models.FileField(upload_to="covers/", blank=True)
    status = models.CharField(
        max_length=9, choices=PublicationStatus.choices, default=PublicationStatus.DRAFT
    )
    is_paid = models.BooleanField(default=False)
    price_npr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(is_paid=False, price_npr=0)
                | models.Q(is_paid=True, price_npr__gt=0),
                name="course_valid_price",
            )
        ]
        indexes = [models.Index(fields=["status", "subject"])]

    def __str__(self):
        return self.title


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    sort_order = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title


class Material(models.Model):
    class Kind(models.TextChoices):
        TEXT = "Text", "Text"
        IMAGE = "Image", "Image"
        PDF = "PDF", "PDF"
        VIDEO = "Video", "Video"
        AUDIO = "Audio", "Audio"
        YOUTUBE = "YouTube", "YouTube"
        CODE = "Code", "Code lab"

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    kind = models.CharField(max_length=7, choices=Kind.choices)
    status = models.CharField(
        max_length=9, choices=PublicationStatus.choices, default=PublicationStatus.DRAFT
    )
    text_content = models.TextField(max_length=10000, blank=True)
    file = models.FileField(upload_to="lessons/", blank=True)
    youtube_url = models.URLField(blank=True, max_length=500)
    alt_text = models.CharField(max_length=150, blank=True)
    is_preview = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["sort_order", "id"]

    @property
    def course(self):
        return self.topic.course

    def __str__(self):
        return self.title
