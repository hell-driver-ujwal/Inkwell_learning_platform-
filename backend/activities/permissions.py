"""Activity access distinguishes author preview from learner participation."""

from accounts.models import UserRole
from common.models import PublicationStatus
from courses.permissions import active_user, can_preview, can_study
from rest_framework.exceptions import PermissionDenied

from activities.models import Activity


def require_activity_access(*, user, activity, preview=False):
    if preview and can_preview(user, activity.course):
        return
    if not preview and activity.status == PublicationStatus.PUBLISHED:
        if can_study(user, activity.course):
            return
        if (
            activity.kind == Activity.Kind.DISCUSSION
            and can_preview(user, activity.course)
            and activity.course.status == PublicationStatus.PUBLISHED
        ):
            return
    raise PermissionDenied("You cannot access this activity.")


def require_attempt_access(*, user, attempt):
    if active_user(user) and (
        user.role == UserRole.ADMIN
        or attempt.learner_id == user.id
        or can_preview(user, attempt.activity.course)
    ):
        return
    raise PermissionDenied("These results are private.")
