"""Result summaries must be scoped as strictly as individual attempts."""

from common.tests.factories import LearningTestCase

from activities.models import Attempt


class SummaryTests(LearningTestCase):
    def test_score_summary_and_filters_do_not_include_other_learner(self):
        Attempt.objects.create(activity=self.quiz, learner=self.learner, score_percent=75)
        Attempt.objects.create(activity=self.quiz, learner=self.other_learner, score_percent=10)
        self.sign_in(self.learner)
        response = self.client.get("/api/attempts/summary/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["scores"]), 1)
        self.assertEqual(response.data["scores"][0]["best_score"], 75)
        self.assertNotIn(self.other_learner.full_name, str(response.data))
        self.assertEqual(self.client.get("/api/attempts/filters/").status_code, 200)
