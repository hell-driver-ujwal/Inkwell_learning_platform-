"""Route publication validation to each activity's own domain rules."""

from games.validation import validate_game
from rest_framework.exceptions import ValidationError
from scenarios.validation import validate_scenario

from activities.models import Activity


def validate_publication(activity):
    if activity.kind == Activity.Kind.QUIZ:
        questions = list(activity.questions.prefetch_related("options"))
        if not questions:
            raise ValidationError("A quiz needs at least one question.")
        for question in questions:
            options = list(question.options.all())
            if not 2 <= len(options) <= 6 or sum(option.is_correct for option in options) != 1:
                raise ValidationError(
                    "Each question needs 2 to 6 options and exactly one correct answer."
                )
    elif activity.kind == Activity.Kind.GAME:
        validate_game(activity)
    elif activity.kind == Activity.Kind.SCENARIO:
        validate_scenario(activity)
    elif activity.kind == Activity.Kind.ASSESSMENT:
        if not activity.statements.exists():
            raise ValidationError("A self assessment needs at least one statement.")
    elif activity.kind == Activity.Kind.DISCUSSION:
        if len(activity.title) < 5 or len(activity.description) < 10:
            raise ValidationError("A discussion needs a title and a meaningful prompt.")
