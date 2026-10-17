"""Results summaries always start with a permission-scoped attempt queryset."""

from assessments.models import Response
from django.db.models import Avg, Count, Max, OuterRef, Subquery


def summarize_attempts(attempts):
    """Keep score summaries, confidence averages and scenario outcomes distinct."""
    latest_score = (
        attempts.filter(activity_id=OuterRef("activity_id"), learner_id=OuterRef("learner_id"))
        .order_by("-submitted_at", "-id")
        .values("score_percent")[:1]
    )
    scores = (
        attempts.filter(score_percent__isnull=False)
        .order_by()
        .values("activity_id", "activity__title", "learner_id", "learner__full_name")
        .annotate(
            attempt_count=Count("id"),
            best_score=Max("score_percent"),
            average_score=Avg("score_percent"),
            latest_score=Subquery(latest_score),
        )
    )
    confidence = (
        Response.objects.filter(attempt__in=attempts)
        .order_by()
        .values("statement__text", "attempt__activity__title")
        .annotate(average_rating=Avg("rating"), response_count=Count("id"))
    )
    endings = (
        attempts.filter(ending_step__isnull=False)
        .order_by()
        .values("activity__title", "ending_step__outcome", "ending_step__text")
        .annotate(attempt_count=Count("id"))
    )
    return {"scores": list(scores), "confidence": list(confidence), "endings": list(endings)}


def confidence_comparison(attempt):
    """Compare this reflection with the same learner's preceding submission."""
    previous = (
        attempt.activity.attempts.filter(
            learner=attempt.learner, submitted_at__lt=attempt.submitted_at
        )
        .order_by("-submitted_at", "-id")
        .first()
    )
    previous_ratings = (
        {rating.statement_id: rating.rating for rating in previous.ratings.all()}
        if previous
        else {}
    )
    return [
        {
            "statement": rating.statement.text,
            "rating": rating.rating,
            "previous_rating": previous_ratings.get(rating.statement_id),
        }
        for rating in attempt.ratings.select_related("statement")
    ]
