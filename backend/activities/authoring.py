"""Atomic authoring operations freeze structure after the first learner attempt."""

from assessments.models import Statement
from common.models import PublicationStatus
from courses.permissions import require_owner
from django.db import transaction
from games.models import Group, Item
from quizzes.models import Option, Question
from rest_framework.exceptions import ValidationError
from scenarios.models import Choice, Step

from activities.models import Activity
from activities.publishing import validate_publication


def require_unlocked(activity):
    """Historical scores must keep their original content and settings."""
    if activity.attempts.exists():
        raise ValidationError(
            "Content is locked after attempts. Title and description remain editable."
        )


@transaction.atomic
def save_activity(*, user, serializer):
    activity = serializer.instance
    structure_changed = activity is None
    if activity:
        activity = Activity.objects.select_for_update().get(pk=activity.pk)
        serializer.instance = activity
        require_owner(user, activity.course)
        if serializer.validated_data.get("kind", activity.kind) != activity.kind:
            raise ValidationError("An existing activity cannot change its type.")
        for field in (
            "topic",
            "kind",
            "sort_order",
            "time_limit_minutes",
            "max_attempts",
            "game_template",
            "start_step",
        ):
            if field in serializer.validated_data and serializer.validated_data[field] != getattr(
                activity, field
            ):
                structure_changed = True
                if activity.attempts.exists():
                    raise ValidationError("Activity structure is locked after attempts.")
        template_changed = (
            serializer.validated_data.get("game_template", activity.game_template)
            != activity.game_template
        )
        if template_changed and (activity.game_items.exists() or activity.game_groups.exists()):
            raise ValidationError("Remove game content before changing its template.")
    topic = serializer.validated_data.get("topic", activity.topic if activity else None)
    require_owner(user, topic.course)
    if activity and topic.pk != activity.topic_id:
        raise ValidationError("Activities cannot move between topics.")
    activity = serializer.save()
    if activity.kind == Activity.Kind.GAME:
        from games.models import GameTemplate

        if activity.game_template not in GameTemplate.values:
            raise ValidationError("Choose a valid game template.")
    if activity.status == PublicationStatus.PUBLISHED:
        validate_publication(activity)
    if structure_changed:
        activity.revision += 1
        activity.save(update_fields=["revision"])
    return activity


@transaction.atomic
def replace_content(*, user, activity_id, content):
    """Validate a whole editor save so a half-written quiz or graph never becomes visible."""
    activity = Activity.objects.select_for_update().get(pk=activity_id)
    require_owner(user, activity.course)
    require_unlocked(activity)
    if activity.kind == Activity.Kind.QUIZ:
        activity.questions.all().delete()
        for question_data in content:
            options = question_data.pop("options")
            question = Question.objects.create(activity=activity, **question_data)
            Option.objects.bulk_create([Option(question=question, **option) for option in options])
    elif activity.kind == Activity.Kind.ASSESSMENT:
        activity.statements.all().delete()
        Statement.objects.bulk_create(
            [Statement(activity=activity, **statement) for statement in content]
        )
    elif activity.kind == Activity.Kind.GAME:
        activity.game_items.all().delete()
        activity.game_groups.all().delete()
        groups = {}
        for group_data in content["groups"]:
            groups[group_data["key"]] = Group.objects.create(
                activity=activity, name=group_data["name"]
            )
        for item in content["items"]:
            Item.objects.create(
                activity=activity,
                group=groups.get(item.get("group_key")),
                text=item["text"],
                match_text=item["match_text"],
            )
    elif activity.kind == Activity.Kind.SCENARIO:
        existing_images = {
            str(step.id): (step.image.name, step.image_alt) for step in activity.steps.all()
        }
        activity.start_step = None
        activity.save(update_fields=["start_step"])
        Choice.objects.filter(from_step__activity=activity).delete()
        activity.steps.all().delete()
        steps = {}
        for step_data in content["steps"]:
            key = step_data.pop("key")
            image_name, image_alt = existing_images.get(key, ("", ""))
            steps[key] = Step.objects.create(
                activity=activity, image=image_name, image_alt=image_alt, **step_data
            )
        for choice in content["choices"]:
            Choice.objects.create(
                from_step=steps[choice["from_key"]],
                next_step=steps[choice["next_key"]],
                text=choice["text"],
            )
        activity.start_step = steps[content["start_key"]]
    else:
        raise ValidationError("This activity has no structured content editor.")
    if activity.status == PublicationStatus.PUBLISHED:
        validate_publication(activity)
    activity.revision += 1
    activity.save(update_fields=["revision", "start_step"])
    return activity
