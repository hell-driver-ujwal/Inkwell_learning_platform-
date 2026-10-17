"""Scenario publication checks allow loops but reject broken destinations."""

from rest_framework.exceptions import ValidationError

from scenarios.models import Step


def validate_scenario(activity):
    steps = list(activity.steps.prefetch_related("choices"))
    identifiers = {step.id for step in steps}
    if activity.start_step_id not in identifiers or not any(step.is_ending for step in steps):
        raise ValidationError("Choose a start step and at least one ending.")
    for step in steps:
        choices = list(step.choices.all())
        if len(step.text.strip()) < 10:
            raise ValidationError("Step text needs at least ten characters.")
        if step.image and len(step.image_alt.strip()) < 5:
            raise ValidationError("Scenario images need descriptive alternative text.")
        if step.is_ending:
            if (
                choices
                or step.outcome not in Step.Outcome.values
                or len(step.feedback.strip()) < 10
            ):
                raise ValidationError("Endings need an outcome, feedback and no outgoing choices.")
        elif not choices:
            raise ValidationError("Every non-ending step needs a choice.")
        for choice in choices:
            if choice.next_step_id not in identifiers or choice.next_step_id == step.id:
                raise ValidationError("Choices must point to a different step in this scenario.")
