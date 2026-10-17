"""Server-owned play sessions, timers and atomic submission coordination."""

from datetime import timedelta

from assessments.models import Response as AssessmentResponse
from assessments.services import assess_ratings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from games.scoring import score_game
from quizzes.models import Answer
from quizzes.scoring import score_quiz
from rest_framework.exceptions import ValidationError

from activities.models import Activity, Attempt, PlaySession
from activities.permissions import require_activity_access


def check_attempt_limit(user, activity, preview):
    """Only completed real quiz attempts count toward the original attempt limit."""
    if not preview and activity.kind == Activity.Kind.QUIZ and activity.max_attempts:
        if activity.attempts.filter(learner=user).count() >= activity.max_attempts:
            raise ValidationError("No attempts remain.")


@transaction.atomic
def start_activity(*, user, activity_id, preview=False):
    """Lock the activity so author edits and simultaneous starts cannot race."""
    from activities.publishing import validate_publication

    activity = get_object_or_404(Activity.objects.select_for_update(), pk=activity_id)
    require_activity_access(user=user, activity=activity, preview=preview)
    validate_publication(activity)
    check_attempt_limit(user, activity, preview)
    unfinished = PlaySession.objects.filter(
        activity=activity, user=user, preview=preview, finished=False
    )
    for run in unfinished:
        expired = activity.time_limit_minutes and timezone.now() > run.started_at + timedelta(
            minutes=activity.time_limit_minutes, seconds=30
        )
        if run.revision == activity.revision and not expired:
            return run
        run.finished = True
        run.save(update_fields=["finished"])
    return PlaySession.objects.create(
        activity=activity,
        user=user,
        preview=preview,
        revision=activity.revision,
        current_step=activity.start_step if activity.kind == Activity.Kind.SCENARIO else None,
    )


def locked_run(*, user, run_id):
    """Caller must hold a transaction; always lock activity before session."""
    candidate = get_object_or_404(PlaySession, pk=run_id, user=user)
    activity = Activity.objects.select_for_update().get(pk=candidate.activity_id)
    run = PlaySession.objects.select_for_update().get(pk=run_id, user=user)
    run.activity = activity
    require_activity_access(user=user, activity=activity, preview=run.preview)
    if run.revision != activity.revision:
        raise ValidationError("Content changed. Start again before continuing.")
    return run


@transaction.atomic
def submit_activity(*, user, run_id, answers=None, game_answers=None, ratings=None, moves=None):
    """Save score and answer rows together; a repeated submission returns its first result."""
    run = locked_run(user=user, run_id=run_id)
    if run.finished:
        if run.result:
            return run
        raise ValidationError("This run expired. Start again.")
    activity = run.activity
    elapsed = max(0, int((timezone.now() - run.started_at).total_seconds()))
    check_attempt_limit(user, activity, run.preview)
    score = None
    result = {}
    if activity.kind == Activity.Kind.QUIZ:
        if activity.time_limit_minutes and elapsed > activity.time_limit_minutes * 60 + 30:
            raise ValidationError("Time expired. Nothing was saved; restart if attempts remain.")
        score, review = score_quiz(
            questions=list(activity.questions.prefetch_related("options")), answers=answers or []
        )
        result = {"score_percent": str(score), "review": review}
    elif activity.kind == Activity.Kind.GAME:
        score = score_game(
            template=activity.game_template,
            items=list(activity.game_items.all()),
            groups=list(activity.game_groups.all()),
            answers=game_answers or [],
            elapsed_seconds=elapsed,
            moves=moves,
        )
        result = {"score_percent": str(score)}
    elif activity.kind == Activity.Kind.ASSESSMENT:
        result = assess_ratings(statements=list(activity.statements.all()), ratings=ratings or [])
    else:
        raise ValidationError("Use the discussion or scenario endpoint for this activity.")
    if not run.preview:
        attempt = Attempt.objects.create(
            activity=activity, learner=user, score_percent=score, time_taken_seconds=elapsed
        )
        if activity.kind == Activity.Kind.QUIZ:
            Answer.objects.bulk_create(
                [
                    Answer(
                        attempt=attempt,
                        question_id=answer["question_id"],
                        selected_option_id=answer["selected_option"],
                    )
                    for answer in result["review"]
                ]
            )
        elif activity.kind == Activity.Kind.ASSESSMENT:
            AssessmentResponse.objects.bulk_create(
                [AssessmentResponse(attempt=attempt, **rating) for rating in ratings]
            )
        run.attempt = attempt
        result["attempt_id"] = attempt.id
    run.result = result
    run.finished = True
    run.save(update_fields=["attempt", "result", "finished"])
    return run
