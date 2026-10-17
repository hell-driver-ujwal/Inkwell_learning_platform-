"""Discussion ownership, moderation and one-level reply rules."""

from accounts.models import UserRole
from activities.models import Activity
from activities.permissions import require_activity_access
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError


def require_post_permission(user, activity, post=None, deleting=False):
    require_activity_access(user=user, activity=activity)
    if activity.kind != Activity.Kind.DISCUSSION:
        raise ValidationError("This activity is not a discussion.")
    owner = activity.course.teacher_id == user.id
    moderator = user.role == UserRole.ADMIN or (user.role == UserRole.TEACHER and owner)
    if deleting and moderator:
        return
    if activity.is_closed or (user.role == UserRole.ADMIN and not owner):
        raise PermissionDenied("This discussion is closed or read-only for your account.")
    if post and post.user_id != user.id:
        raise PermissionDenied("You can only edit your own posts.")


@transaction.atomic
def save_post(*, user, serializer):
    activity = serializer.validated_data.get(
        "activity", serializer.instance.activity if serializer.instance else None
    )
    activity = Activity.objects.select_for_update().get(pk=activity.pk)
    require_post_permission(user, activity, serializer.instance)
    parent = serializer.validated_data.get("parent")
    if parent and (parent.activity_id != activity.id or parent.parent_id is not None):
        raise ValidationError("Reply to a top-level post in this discussion.")
    if serializer.instance and serializer.instance.activity_id != activity.id:
        raise ValidationError("Posts cannot move between discussions.")
    return serializer.save(user=user, activity=activity)


@transaction.atomic
def delete_post(*, user, post):
    activity = Activity.objects.select_for_update().get(pk=post.activity_id)
    require_post_permission(user, activity, post, deleting=True)
    post.delete()
