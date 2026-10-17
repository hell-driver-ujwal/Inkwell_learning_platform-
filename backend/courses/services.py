"""Authoring and publication actions enforce ownership inside transactions."""

from common.models import PublicationStatus
from django.db import transaction
from rest_framework.exceptions import ValidationError

from courses.models import Course
from courses.permissions import require_owner


@transaction.atomic
def save_course(*, user, serializer):
    if serializer.instance:
        serializer.instance = Course.objects.select_for_update().get(pk=serializer.instance.pk)
        require_owner(user, serializer.instance)
    course = serializer.save(teacher=user)
    if course.status == PublicationStatus.PUBLISHED:
        lessons = course.topics.filter(materials__status=PublicationStatus.PUBLISHED).exists()
        activities = course.topics.filter(activities__status=PublicationStatus.PUBLISHED).exists()
        if not lessons and not activities:
            raise ValidationError(
                "Publish at least one lesson or activity before publishing the course."
            )
    return course
