"""Role-scoped dashboard summaries and anonymous analytics aggregates."""

from datetime import timedelta
from datetime import timezone as datetime_timezone

from accounts.models import User, UserRole
from activities.models import Attempt
from courses.models import Course
from discussions.models import Post
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from learning.models import Completion, Enrollment
from learning.selectors import course_progress

from analytics.models import PageView


def dashboard_for(user):
    courses = Course.objects.all()
    attempts = Attempt.objects.select_related("activity", "learner")
    if user.role == UserRole.LEARNER:
        courses = courses.filter(enrollments__learner=user)
        attempts = attempts.filter(learner=user)
    elif user.role == UserRole.TEACHER:
        courses = courses.filter(teacher=user)
        attempts = attempts.filter(activity__topic__course__teacher=user)
    data = {
        "course_count": courses.count(),
        "attempt_count": attempts.count(),
        "attempts_this_week": attempts.filter(
            submitted_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        "learner_count": Enrollment.objects.filter(course__in=courses)
        .values("learner")
        .distinct()
        .count(),
        "post_count": Post.objects.filter(activity__topic__course__in=courses).count(),
    }
    if user.role == UserRole.LEARNER:
        data["courses"] = [
            {
                "id": course.id,
                "title": course.title,
                "progress": course_progress(learner=user, course=course),
            }
            for course in courses
        ]
        days = set(
            attempts.annotate(
                day=TruncDate("submitted_at", tzinfo=datetime_timezone.utc)
            ).values_list("day", flat=True)
        )
        days.update(
            Completion.objects.filter(learner=user)
            .annotate(day=TruncDate("created_at", tzinfo=datetime_timezone.utc))
            .values_list("day", flat=True)
        )
        days.update(
            Post.objects.filter(user=user)
            .annotate(day=TruncDate("created_at", tzinfo=datetime_timezone.utc))
            .values_list("day", flat=True)
        )
        day = timezone.now().date()
        if day not in days:
            day -= timedelta(days=1)
        streak = 0
        while day in days:
            streak += 1
            day -= timedelta(days=1)
        data["streak"] = streak
    if user.role == UserRole.ADMIN:
        data["user_count"] = User.objects.count()
        data["pending_teachers"] = User.objects.filter(
            role=UserRole.TEACHER, status="Pending"
        ).count()
    return data


def page_statistics():
    return {
        "pages": list(
            PageView.objects.values("path").annotate(count=Count("id")).order_by("-count")[:30]
        ),
        "roles": list(PageView.objects.values("viewer_role").annotate(count=Count("id"))),
        "days": list(
            PageView.objects.annotate(day=TruncDate("viewed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        ),
    }
