"""Examples of all eight scoring algorithms and invalid-answer rejection."""

from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from games.scoring import score_game


class GameScoringTests(SimpleTestCase):
    def item(self, identifier, text, match="", group=None):
        return SimpleNamespace(id=identifier, text=text, match_text=match, group_id=group)

    def score(self, template, items, answers=None, **kwargs):
        return score_game(
            template=template,
            items=items,
            groups=kwargs.pop("groups", []),
            answers=answers or [],
            elapsed_seconds=kwargs.pop("elapsed_seconds", 0),
            **kwargs,
        )

    def test_matching(self):
        items = [self.item(1, "A"), self.item(2, "B")]
        self.assertEqual(
            self.score(
                "Matching", items, [{"item_id": 1, "value": "1"}, {"item_id": 2, "value": "2"}]
            ),
            100,
        )

    def test_memory_move_and_time_penalty(self):
        items = [self.item(1, "A"), self.item(2, "B")]
        self.assertEqual(self.score("Memory", items, moves=4, elapsed_seconds=39), 87)
        self.assertEqual(self.score("Memory", items, moves=1000000), 0)

    def test_flashcards_are_self_rated(self):
        self.assertEqual(
            self.score("Flashcards", [self.item(1, "A")], [{"item_id": 1, "value": "learning"}]), 0
        )
        self.assertEqual(
            self.score("Flashcards", [self.item(1, "A")], [{"item_id": 1, "value": "known"}]), 100
        )

    def test_scramble_ignores_case(self):
        self.assertEqual(
            self.score("Scramble", [self.item(1, "Python")], [{"item_id": 1, "value": "PYTHON"}]),
            100,
        )

    def test_fill_blank_normalizes_whitespace(self):
        self.assertEqual(
            self.score(
                "FillBlank",
                [self.item(1, "machine learning")],
                [{"item_id": 1, "value": " Machine   Learning "}],
            ),
            100,
        )

    def test_true_false_skip_earns_zero(self):
        self.assertEqual(
            self.score("TrueFalse", [self.item(1, "True")], [{"item_id": 1, "value": "Skip"}]), 0
        )

    def test_sort_checks_group_membership(self):
        items = [self.item(1, "A", group=7)]
        groups = [SimpleNamespace(id=7)]
        self.assertEqual(
            self.score("Sort", items, [{"item_id": 1, "value": "7"}], groups=groups), 100
        )
        with self.assertRaises(ValidationError):
            self.score("Sort", items, [{"item_id": 1, "value": "999"}], groups=groups)

    def test_sequence_requires_unique_positions(self):
        items = [self.item(1, "First", "1"), self.item(2, "Second", "2")]
        self.assertEqual(
            self.score(
                "Sequence", items, [{"item_id": 1, "value": "2"}, {"item_id": 2, "value": "1"}]
            ),
            0,
        )
        with self.assertRaises(ValidationError):
            self.score(
                "Sequence", items, [{"item_id": 1, "value": "1"}, {"item_id": 2, "value": "1"}]
            )

    def test_duplicate_or_foreign_items_rejected(self):
        with self.assertRaises(ValidationError):
            self.score("Matching", [self.item(1, "A")], [{"item_id": 999, "value": "1"}])
