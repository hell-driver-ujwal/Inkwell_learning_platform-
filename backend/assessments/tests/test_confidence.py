"""Confidence thresholds and complete statement coverage."""

from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from assessments.services import assess_ratings


class AssessmentTests(SimpleTestCase):
    def test_feedback_bands(self):
        for rating, expected in [(2, "Needs Improvement"), (3, "Developing"), (4, "Confident")]:
            result = assess_ratings(
                statements=[SimpleNamespace(id=1)], ratings=[{"statement_id": 1, "rating": rating}]
            )
            self.assertEqual(result["level"], expected)

    def test_duplicate_statement_rejected(self):
        with self.assertRaises(ValidationError):
            assess_ratings(
                statements=[SimpleNamespace(id=1)],
                ratings=[{"statement_id": 1, "rating": 3}, {"statement_id": 1, "rating": 3}],
            )
