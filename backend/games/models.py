"""Typed game content; scoring lives separately in scoring.py."""

from django.db import models


class GameTemplate(models.TextChoices):
    MATCHING = "Matching", "Matching"
    MEMORY = "Memory", "Memory"
    FLASHCARDS = "Flashcards", "Flashcards"
    SCRAMBLE = "Scramble", "Word scramble"
    SORT = "Sort", "Sort into groups"
    FILL_BLANK = "FillBlank", "Fill in the blank"
    TRUE_FALSE = "TrueFalse", "True or false"
    SEQUENCE = "Sequence", "Put in order"


class Group(models.Model):
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, related_name="game_groups"
    )
    name = models.CharField(max_length=50)


class Item(models.Model):
    activity = models.ForeignKey(
        "activities.Activity", on_delete=models.CASCADE, related_name="game_items"
    )
    group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.PROTECT)
    text = models.CharField(max_length=100)
    match_text = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["id"]
