"""Server scoring, timers, attempt limits and answer-key privacy."""

from datetime import timedelta

from activities.authoring import replace_content
from activities.models import Attempt, PlaySession
from activities.services import start_activity, submit_activity
from common.tests.factories import LearningTestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from quizzes.models import Option, Question
from quizzes.scoring import score_quiz


class QuizTests(LearningTestCase):
    def test_weighted_score_and_unanswered_question(self):
        second = Question.objects.create(
            activity=self.quiz, text="An unanswered question?", marks=1
        )
        Option.objects.create(question=second, text="Yes", is_correct=True)
        Option.objects.create(question=second, text="No")
        score, review = score_quiz(
            questions=list(self.quiz.questions.prefetch_related("options")),
            answers=[{"question_id": self.question.id, "option_id": self.correct.id}],
        )
        self.assertEqual(score, 75)
        self.assertIsNone(review[1]["selected_option"])

    def test_foreign_option_rejected(self):
        second = Question.objects.create(activity=self.quiz, text="Another question?")
        foreign = Option.objects.create(question=second, text="Elsewhere", is_correct=True)
        with self.assertRaises(ValidationError):
            score_quiz(
                questions=[self.question],
                answers=[{"question_id": self.question.id, "option_id": foreign.id}],
            )

    def test_duplicate_answers_rejected(self):
        answer = {"question_id": self.question.id, "option_id": self.correct.id}
        with self.assertRaises(ValidationError):
            score_quiz(questions=[self.question], answers=[answer, answer])

    def test_start_does_not_reset_timer(self):
        first = start_activity(user=self.learner, activity_id=self.quiz.id)
        second = start_activity(user=self.learner, activity_id=self.quiz.id)
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.started_at, second.started_at)

    def test_submission_is_atomic_idempotent_and_limited(self):
        run = start_activity(user=self.learner, activity_id=self.quiz.id)
        answers = [{"question_id": self.question.id, "option_id": self.correct.id}]
        result = submit_activity(user=self.learner, run_id=run.id, answers=answers)
        retry = submit_activity(user=self.learner, run_id=run.id, answers=[])
        self.assertEqual(result.attempt_id, retry.attempt_id)
        self.assertEqual(result.attempt.quiz_answers.count(), 1)
        self.assertEqual(Attempt.objects.count(), 1)
        with self.assertRaises(ValidationError):
            start_activity(user=self.learner, activity_id=self.quiz.id)

    def test_expired_submission_saves_nothing(self):
        self.quiz.time_limit_minutes = 1
        self.quiz.save()
        run = start_activity(user=self.learner, activity_id=self.quiz.id)
        PlaySession.objects.filter(pk=run.pk).update(
            started_at=timezone.now() - timedelta(seconds=91)
        )
        with self.assertRaises(ValidationError):
            submit_activity(user=self.learner, run_id=run.id, answers=[])
        self.assertEqual(Attempt.objects.count(), 0)

    def test_preview_never_counts_as_attempt(self):
        run = start_activity(user=self.teacher, activity_id=self.quiz.id, preview=True)
        result = submit_activity(user=self.teacher, run_id=run.id, answers=[])
        self.assertTrue(result.finished)
        self.assertIsNone(result.attempt_id)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_answer_keys_hidden_before_submission(self):
        self.sign_in(self.learner)
        payload = self.client.get(f"/api/activities/{self.quiz.id}/").data
        self.assertNotIn("is_correct", str(payload))
        self.assertNotIn("correct_option", str(payload))

    def test_content_locked_after_attempt(self):
        Attempt.objects.create(learner=self.learner, activity=self.quiz)
        with self.assertRaises(ValidationError):
            replace_content(user=self.teacher, activity_id=self.quiz.id, content=[])
        self.assertEqual(self.quiz.questions.count(), 1)
