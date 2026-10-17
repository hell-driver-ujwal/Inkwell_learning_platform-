"""The same progress definition drives ticks, dashboards and certificates."""

from decimal import ROUND_HALF_UP, Decimal

from activities.models import Activity, Attempt
from common.models import PublicationStatus
from courses.models import Material
from discussions.models import Post

from learning.models import Completion


def course_progress(*, learner, course):
    """Count published lessons and activities once, regardless of score or retries."""
    materials = set(
        Material.objects.filter(
            topic__course=course, status=PublicationStatus.PUBLISHED
        ).values_list("id", flat=True)
    )
    activities = set(
        Activity.objects.filter(
            topic__course=course, status=PublicationStatus.PUBLISHED
        ).values_list("id", flat=True)
    )
    completed_materials = set(
        Completion.objects.filter(learner=learner, material_id__in=materials).values_list(
            "material_id", flat=True
        )
    )
    completed_activities = set(
        Attempt.objects.filter(learner=learner, activity_id__in=activities).values_list(
            "activity_id", flat=True
        )
    )
    completed_activities.update(
        Post.objects.filter(user=learner, activity_id__in=activities).values_list(
            "activity_id", flat=True
        )
    )
    total = len(materials) + len(activities)
    completed = len(completed_materials) + len(completed_activities)
    percent = (
        (Decimal(completed * 100) / total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if total
        else Decimal(0)
    )
    return {
        "percent": percent,
        "completed": completed,
        "total": total,
        "materials": sorted(completed_materials),
        "activities": sorted(completed_activities),
    }
