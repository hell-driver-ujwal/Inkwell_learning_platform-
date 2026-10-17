"""The eight original game scoring rules, independent of HTTP requests."""

import re
from decimal import ROUND_HALF_UP, Decimal

from rest_framework.exceptions import ValidationError

from games.models import GameTemplate


def normalize_answer(value):
    """Typed answers ignore case and repeated whitespace."""
    return " ".join(value.split()).casefold()


def score_game(*, template, items, groups, answers, elapsed_seconds, moves=None):
    """Recompute a score from submitted actions, never a browser-supplied score."""
    if not items:
        raise ValidationError("This game has no items.")
    if template == GameTemplate.MEMORY:
        if answers or moves is None or moves < len(items):
            raise ValidationError("Memory requires no answers and at least one move per pair.")
        return Decimal(max(0, 100 - 5 * (moves - len(items)) - elapsed_seconds // 10))
    if moves is not None or len(answers) != len(items):
        raise ValidationError("Submit exactly one answer per item. Moves are Memory-only.")
    item_ids = {item.id for item in items}
    group_ids = {group.id for group in groups}
    submitted = {}
    for answer in answers:
        item_id = answer["item_id"]
        if item_id not in item_ids or item_id in submitted:
            raise ValidationError("Unknown or duplicate game item.")
        submitted[item_id] = answer["value"]
    used_targets = set()
    correct = 0
    for item in items:
        value = submitted[item.id]
        if template == GameTemplate.FLASHCARDS:
            if value not in ("known", "learning"):
                raise ValidationError("Rate each card as known or learning.")
            right = value == "known"
        elif template == GameTemplate.FILL_BLANK:
            if len(value.strip()) > 100:
                raise ValidationError("An answer is too long.")
            right = normalize_answer(value) == normalize_answer(item.text)
        elif template == GameTemplate.TRUE_FALSE:
            if value not in ("True", "False", "Skip"):
                raise ValidationError("Choose True or False.")
            right = value == item.text
        elif template == GameTemplate.SCRAMBLE:
            if value.strip() and not re.fullmatch(r"[A-Za-z]{3,15}", value.strip()):
                raise ValidationError("Use 3 to 15 letters for scramble answers.")
            right = value.strip().casefold() == item.text.strip().casefold()
        else:
            if not value.isascii() or not value.isdigit():
                raise ValidationError("Choose a valid target or position.")
            target = int(value)
            if template == GameTemplate.SEQUENCE:
                if target not in range(1, len(items) + 1) or target in used_targets:
                    raise ValidationError("Use every position exactly once.")
                right = target == int(item.match_text)
            elif template == GameTemplate.MATCHING:
                if target not in item_ids or target in used_targets:
                    raise ValidationError("Use each matching target exactly once.")
                right = target == item.id
            elif template == GameTemplate.SORT:
                if target not in group_ids:
                    raise ValidationError("Choose a group from this game.")
                right = target == item.group_id
            else:
                raise ValidationError("Unknown game template.")
            used_targets.add(target)
        correct += int(right)
    return (Decimal(correct * 100) / len(items)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
