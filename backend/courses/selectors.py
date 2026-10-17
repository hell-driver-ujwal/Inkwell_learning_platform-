"""Catalogue visibility and safe curriculum outlines."""

from accounts.models import UserRole
from common.models import PublicationStatus
from django.db.models import Q

from courses.models import Course
from courses.permissions import active_user, can_preview


def visible_courses(user):
    courses = Course.objects.select_related("teacher", "subject")
    if active_user(user) and user.role == UserRole.ADMIN:
        return courses
    if active_user(user) and user.role == UserRole.TEACHER:
        return courses.filter(Q(status=PublicationStatus.PUBLISHED) | Q(teacher=user))
    return courses.filter(status=PublicationStatus.PUBLISHED)


def curriculum(*, user, course):
    """Public outlines reveal titles, never protected material bodies or answer keys."""
    preview = can_preview(user, course)
    topics = []
    for topic in course.topics.prefetch_related("materials", "activities"):
        materials = []
        activities = []
        for material in topic.materials.all():
            if preview or material.status == PublicationStatus.PUBLISHED:
                materials.append(
                    {
                        "id": material.id,
                        "title": material.title,
                        "kind": material.kind,
                        "is_preview": material.is_preview,
                        "status": material.status,
                    }
                )
        for activity in topic.activities.all():
            if preview or activity.status == PublicationStatus.PUBLISHED:
                activities.append(
                    {
                        "id": activity.id,
                        "title": activity.title,
                        "kind": activity.kind,
                        "game_template": activity.game_template,
                        "status": activity.status,
                    }
                )
        topics.append(
            {
                "id": topic.id,
                "title": topic.title,
                "sort_order": topic.sort_order,
                "materials": materials,
                "activities": activities,
            }
        )
    return topics
