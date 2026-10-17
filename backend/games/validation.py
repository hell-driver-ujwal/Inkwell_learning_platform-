"""Publication rules for each of the eight game templates."""

import re

from rest_framework.exceptions import ValidationError

from games.models import GameTemplate


def validate_game(activity):
    """Keep published games playable and reject ambiguous answer definitions."""
    template = activity.game_template
    items = list(activity.game_items.all())
    groups = list(activity.game_groups.all())
    maximum = {"Memory": 12, "Sequence": 10, "FillBlank": 15, "TrueFalse": 20}.get(template, 30)
    minimum = 3 if template in ("Scramble", "FillBlank", "Sequence") else 4
    if template not in GameTemplate.values or not minimum <= len(items) <= maximum:
        raise ValidationError(f"This template requires {minimum} to {maximum} valid items.")
    if template == GameTemplate.SORT:
        if not 2 <= len(groups) <= 4:
            raise ValidationError("Sort requires two to four groups.")
        for group in groups:
            if sum(item.group_id == group.id for item in items) < 2:
                raise ValidationError("Each group requires at least two items.")
    texts = set()
    matches = set()
    for item in items:
        text = item.text.strip()
        match = item.match_text.strip()
        if not text:
            raise ValidationError("Every item needs text.")
        if template not in (GameTemplate.TRUE_FALSE, GameTemplate.FILL_BLANK):
            if text.casefold() in texts:
                raise ValidationError("Item texts must be distinct.")
            texts.add(text.casefold())
        if template == GameTemplate.SORT:
            if item.group_id not in {group.id for group in groups}:
                raise ValidationError("Each item needs a group from this game.")
        elif not match:
            raise ValidationError("Every item needs a match, hint, sentence or position.")
        if template in (
            GameTemplate.MATCHING,
            GameTemplate.MEMORY,
            GameTemplate.FILL_BLANK,
            GameTemplate.TRUE_FALSE,
            GameTemplate.SEQUENCE,
        ):
            if match.casefold() in matches:
                raise ValidationError("Matching values must be distinct.")
            matches.add(match.casefold())
        if template == GameTemplate.SCRAMBLE and not re.fullmatch(r"[A-Za-z]{3,15}", text):
            raise ValidationError("Scramble words must contain 3 to 15 letters.")
        if template == GameTemplate.FILL_BLANK and match.count("___") != 1:
            raise ValidationError("Each sentence needs exactly one ___ blank.")
        if template == GameTemplate.TRUE_FALSE and text not in ("True", "False"):
            raise ValidationError("The answer must be True or False.")
        if template == GameTemplate.SEQUENCE and (
            not match.isdigit() or int(match) not in range(1, len(items) + 1)
        ):
            raise ValidationError("Positions must run from one to the item count without gaps.")
