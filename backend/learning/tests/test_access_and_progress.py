"""Enrollment, public previews, durable progress and result privacy."""

from activities.models import Attempt
from common.tests.factories import LearningTestCase
from rest_framework.exceptions import PermissionDenied

from learning.models import Completion, Enrollment
from learning.selectors import course_progress
from learning.services import complete_material, enroll_learner, leave_course


class LearningAccessTests(LearningTestCase):
    def test_paid_course_needs_verified_payment(self):
        self.course.is_paid = True
        self.course.price_npr = 499
        self.course.save()
        with self.assertRaises(PermissionDenied):
            enroll_learner(learner=self.other_learner, course=self.course)
        self.assertFalse(Enrollment.objects.filter(learner=self.other_learner).exists())

    def test_free_enrollment_is_idempotent(self):
        first = enroll_learner(learner=self.other_learner, course=self.course)
        second = enroll_learner(learner=self.other_learner, course=self.course)
        self.assertEqual(first.id, second.id)

    def test_leaving_preserves_results_and_completions(self):
        complete_material(learner=self.learner, material=self.material)
        attempt = Attempt.objects.create(learner=self.learner, activity=self.quiz, score_percent=50)
        leave_course(learner=self.learner, course=self.course)
        self.assertTrue(Completion.objects.filter(learner=self.learner).exists())
        self.assertTrue(Attempt.objects.filter(pk=attempt.pk).exists())
        enroll_learner(learner=self.learner, course=self.course)
        self.assertEqual(course_progress(learner=self.learner, course=self.course)["percent"], 100)

    def test_progress_counts_each_activity_once_and_ignores_drafts(self):
        Attempt.objects.create(learner=self.learner, activity=self.quiz, score_percent=0)
        Attempt.objects.create(learner=self.learner, activity=self.quiz, score_percent=100)
        self.assertEqual(course_progress(learner=self.learner, course=self.course)["percent"], 50)
        self.material.status = "Draft"
        self.material.save()
        self.assertEqual(course_progress(learner=self.learner, course=self.course)["percent"], 100)

    def test_public_preview_requires_published_course_and_material(self):
        path = f"/api/materials/{self.material.id}/"
        self.assertEqual(self.client.get(path).status_code, 403)
        self.material.is_preview = True
        self.material.save()
        self.assertEqual(self.client.get(path).status_code, 200)
        self.course.status = "Draft"
        self.course.save()
        self.assertEqual(self.client.get(path).status_code, 403)

    def test_public_outline_never_contains_protected_body(self):
        response = self.client.get(f"/api/courses/{self.course.id}/")
        self.assertNotIn(self.material.text_content, str(response.data))
        self.assertNotIn("Correct answer", str(response.data))

    def test_other_teacher_cannot_edit_course(self):
        self.sign_in(self.other_teacher)
        response = self.client.patch(
            f"/api/author/courses/{self.course.id}/", {"title": "Stolen course"}, format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_oversight_does_not_grant_author_editing(self):
        self.sign_in(self.admin)
        self.assertEqual(
            self.client.patch(
                f"/api/author/courses/{self.course.id}/", {"title": "Changed title"}, format="json"
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(f"/api/admin/courses/{self.course.id}/unpublish/").status_code, 200
        )

    def test_attempts_are_private_to_learner_owner_and_admin(self):
        attempt = Attempt.objects.create(learner=self.learner, activity=self.quiz)
        self.sign_in(self.other_learner)
        self.assertEqual(self.client.get(f"/api/attempts/{attempt.pk}/").status_code, 404)
        self.sign_in(self.teacher)
        self.assertEqual(self.client.get(f"/api/attempts/{attempt.pk}/").status_code, 200)

    def test_certificate_requires_complete_published_curriculum(self):
        self.sign_in(self.learner)
        path = f"/api/courses/{self.course.id}/certificate/"
        self.assertEqual(self.client.get(path).status_code, 403)
        complete_material(learner=self.learner, material=self.material)
        Attempt.objects.create(learner=self.learner, activity=self.quiz)
        self.assertEqual(self.client.get(path).status_code, 200)
