"""Build safe play payloads without quiz answer keys or game solutions."""

import random

from games.models import GameTemplate

from activities.models import Activity


def play_content(activity):
    """Select only the fields a learner needs before submitting."""
    if activity.kind == Activity.Kind.QUIZ:
        return {
            "questions": [
                {
                    "id": question.id,
                    "text": question.text,
                    "marks": question.marks,
                    "options": [
                        {"id": option.id, "text": option.text} for option in question.options.all()
                    ],
                }
                for question in activity.questions.prefetch_related("options")
            ]
        }
    if activity.kind == Activity.Kind.ASSESSMENT:
        return {"statements": list(activity.statements.values("id", "text"))}
    if activity.kind == Activity.Kind.GAME:
        items = []
        targets = []
        for item in activity.game_items.all():
            text = item.text
            match = item.match_text
            if activity.game_template in (GameTemplate.FILL_BLANK, GameTemplate.TRUE_FALSE):
                text = ""
            elif activity.game_template == GameTemplate.SCRAMBLE:
                text = "".join(random.sample(item.text, len(item.text)))
            elif activity.game_template == GameTemplate.SEQUENCE:
                match = ""
            elif activity.game_template == GameTemplate.MATCHING:
                targets.append({"id": item.id, "text": match})
                match = ""
            items.append({"id": item.id, "text": text, "match_text": match})
        random.shuffle(items)
        random.shuffle(targets)
        return {
            "items": items,
            "targets": targets,
            "groups": list(activity.game_groups.values("id", "name")),
        }
    return {}


def run_payload(run):
    payload = {
        "id": str(run.id),
        "started_at": run.started_at,
        "preview": run.preview,
        "finished": run.finished,
        "result": run.result,
        "step_version": run.step_version,
    }
    if run.current_step:
        step = run.current_step
        payload["step"] = {
            "id": step.id,
            "text": step.text,
            "is_ending": step.is_ending,
            "outcome": step.outcome,
            "feedback": step.feedback,
            "image_url": f"/api/scenario-images/{step.id}/" if step.image else None,
            "image_alt": step.image_alt,
            "choices": list(step.choices.values("id", "text")),
        }
    return payload
