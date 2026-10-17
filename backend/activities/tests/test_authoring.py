"""Authoring rollback, changed definitions and owner isolation."""

from common.tests.factories import LearningTestCase
from rest_framework.exceptions import ValidationError

from activities.authoring import replace_content
from activities.services import start_activity, submit_activity


class AuthoringTests(LearningTestCase):
    def test_invalid_published_quiz_edit_rolls_back(self):
        with self.assertRaises(ValidationError):
            replace_content(user=self.teacher, activity_id=self.quiz.id, content=[])
        self.assertEqual(self.quiz.questions.count(), 1)

    def test_changed_definition_invalidates_inflight_run(self):
        run = start_activity(user=self.learner, activity_id=self.quiz.id)
        content = [
            {
                "text": "A replacement question?",
                "marks": 1,
                "sort_order": 1,
                "options": [
                    {"text": "Yes", "is_correct": True},
                    {"text": "No", "is_correct": False},
                ],
            }
        ]
        replace_content(user=self.teacher, activity_id=self.quiz.id, content=content)
        with self.assertRaises(ValidationError):
            submit_activity(user=self.learner, run_id=run.id, answers=[])

    def test_cross_owner_topic_injection_is_rejected(self):
        self.sign_in(self.other_teacher)
        response = self.client.post(
            "/api/author/activities/",
            {"topic": self.topic.id, "kind": "Quiz", "title": "Injected quiz"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_foreign_run_is_not_accepted(self):
        run = start_activity(user=self.learner, activity_id=self.quiz.id)
        self.sign_in(self.other_learner)
        response = self.client.post(
            f"/api/activities/{self.quiz.id}/submit/",
            {"run_id": str(run.id), "answers": []},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_title_change_does_not_invalidate_an_inflight_quiz(self):
        run = start_activity(user=self.learner, activity_id=self.quiz.id)
        self.sign_in(self.teacher)
        response = self.client.patch(
            f"/api/author/activities/{self.quiz.id}/",
            {"title": "A clearer quiz title"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.revision, run.revision)
