"""Explicit deletion order protects history and handles scenario graph references."""

from accounts.models import UserRole
from activities.models import Activity
from discussions.models import Post
from django.db import transaction
from games.models import Item
from payments.models import Payment
from rest_framework.exceptions import PermissionDenied, ValidationError
from scenarios.models import Choice

from courses.models import Course, Topic
from courses.permissions import active_user, owns_course


def require_delete_access(user, course):
    """Admins may remove unused content; editing still belongs to its author."""
    if owns_course(user, course) or (active_user(user) and user.role == UserRole.ADMIN):
        return
    raise PermissionDenied("Only the author or an administrator may delete this content.")


def delete_activity_records(activity):
    """Caller locks the activity; never remove a definition with saved attempts."""
    if activity.attempts.exists():
        raise ValidationError("This content has attempts. Unpublish it instead.")
    Post.objects.filter(activity=activity).delete()
    Choice.objects.filter(from_step__activity=activity).delete()
    Item.objects.filter(activity=activity).delete()
    activity.start_step = None
    activity.save(update_fields=["start_step"])
    activity.delete()


@transaction.atomic
def delete_activity(*, user, activity):
    activity = Activity.objects.select_for_update().get(pk=activity.pk)
    require_delete_access(user, activity.course)
    delete_activity_records(activity)


@transaction.atomic
def delete_topic(*, user, topic):
    topic = Topic.objects.select_for_update().get(pk=topic.pk)
    require_delete_access(user, topic.course)
    # Lock in primary-key order so simultaneous deletion/submission has a stable order.
    for activity in topic.activities.select_for_update().order_by("pk"):
        delete_activity_records(activity)
    topic.delete()


@transaction.atomic
def delete_course(*, user, course):
    course = Course.objects.select_for_update().get(pk=course.pk)
    require_delete_access(user, course)
    if Payment.objects.filter(course=course).exists():
        raise ValidationError("Payment history must be retained. Unpublish this course instead.")
    activities = Activity.objects.select_for_update().filter(topic__course=course).order_by("pk")
    for activity in activities:
        delete_activity_records(activity)
    course.delete()
