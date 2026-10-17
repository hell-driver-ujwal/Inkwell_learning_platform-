"""Validate every transition against the server's current scenario step."""

from activities.models import Activity, Attempt
from activities.services import locked_run
from django.db import transaction
from rest_framework.exceptions import ValidationError


@transaction.atomic
def move_scenario(*, user, run_id, step_version, choice_id=None, finish=False):
    """Version checks reject stale tabs; reaching an ending records one attempt."""
    run = locked_run(user=user, run_id=run_id)
    if run.activity.kind != Activity.Kind.SCENARIO or not run.current_step:
        raise ValidationError("This is not a scenario run.")
    if run.finished:
        return run
    if step_version != run.step_version:
        raise ValidationError("This page is no longer the current step. Reload the scenario.")
    step = run.current_step
    if finish:
        if not step.is_ending or choice_id is not None:
            raise ValidationError("Only a reached ending can be completed.")
    else:
        choice = (
            step.choices.filter(pk=choice_id, next_step__activity=run.activity)
            .select_related("next_step")
            .first()
        )
        if step.is_ending or choice is None:
            raise ValidationError("That choice is not available at the current step.")
        step = choice.next_step
    run.current_step = step
    run.step_version += 1
    if step.is_ending:
        run.finished = True
        run.result = {"outcome": step.outcome, "feedback": step.feedback}
        if not run.preview:
            run.attempt = Attempt.objects.create(
                activity=run.activity, learner=user, ending_step=step
            )
            run.result["attempt_id"] = run.attempt_id
    run.save()
    return run


@transaction.atomic
def save_step_image(*, user, activity_id, step_id, image=None, image_alt="", remove=False):
    """Image changes are structural content and are locked after learner attempts."""
    from activities.authoring import require_unlocked
    from courses.permissions import require_owner
    from django.shortcuts import get_object_or_404

    activity = get_object_or_404(
        Activity.objects.select_for_update(), pk=activity_id, kind=Activity.Kind.SCENARIO
    )
    require_owner(user, activity.course)
    require_unlocked(activity)
    step = get_object_or_404(activity.steps, pk=step_id)
    step.image = "" if remove else image
    step.image_alt = "" if remove else image_alt
    step.save(update_fields=["image", "image_alt"])
    activity.revision += 1
    activity.save(update_fields=["revision"])
    return step
