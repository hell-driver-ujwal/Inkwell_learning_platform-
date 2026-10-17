"""Authentication rules that are easy to accidentally weaken during a rewrite."""

from common.tests.factories import LearningTestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from accounts.models import AccountStatus, UserRole
from accounts.services import authenticate_portal


class AuthenticationTests(LearningTestCase):
    def test_five_failures_are_committed_and_lock_account(self):
        for _ in range(5):
            with self.assertRaises(ValidationError):
                authenticate_portal(
                    email=self.learner.email, password="wrong", role=UserRole.LEARNER
                )
        self.learner.refresh_from_db()
        self.assertEqual(self.learner.failed_login_count, 5)
        self.assertGreater(self.learner.locked_until, timezone.now())
        with self.assertRaises(ValidationError):
            authenticate_portal(
                email=self.learner.email, password="Learning123!", role=UserRole.LEARNER
            )

    def test_correct_password_wrong_portal_does_not_count_as_failure(self):
        with self.assertRaises(ValidationError):
            authenticate_portal(
                email=self.learner.email, password="Learning123!", role=UserRole.TEACHER
            )
        self.learner.refresh_from_db()
        self.assertEqual(self.learner.failed_login_count, 0)

    def test_pending_teacher_cannot_login(self):
        self.teacher.status = AccountStatus.PENDING
        self.teacher.save()
        with self.assertRaises(ValidationError):
            authenticate_portal(
                email=self.teacher.email, password="Learning123!", role=UserRole.TEACHER
            )

    def test_forced_password_change_blocks_business_endpoints(self):
        self.learner.must_change_password = True
        self.learner.save()
        self.sign_in(self.learner)
        self.assertEqual(self.client.get("/api/dashboard/").status_code, 403)
        response = self.client.post(
            "/api/auth/password/",
            {"current_password": "Learning123!", "new_password": "NewLearning789!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/dashboard/").status_code, 200)

    def test_login_requires_csrf_even_for_anonymous_users(self):
        browser = APIClient(enforce_csrf_checks=True)
        body = {"email": self.learner.email, "password": "Learning123!", "role": "Learner"}
        self.assertEqual(browser.post("/api/auth/login/", body).status_code, 403)
        token = browser.get("/api/auth/session/").data["csrf_token"]
        self.assertEqual(
            browser.post("/api/auth/login/", body, HTTP_X_CSRFTOKEN=token).status_code, 200
        )

    def test_registration_cannot_create_admin(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "evil@example.test",
                "full_name": "Not Admin",
                "role": "Admin",
                "password": "Learning123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_cannot_reset_an_admin_peer(self):
        self.sign_in(self.admin)
        response = self.client.post(
            f"/api/admin/users/{self.admin.id}/action/",
            {"action": "reset_password", "password": "NewLearning789!"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_profile_email_is_editable_but_case_insensitively_unique(self):
        self.sign_in(self.learner)
        response = self.client.patch(
            "/api/auth/profile/", {"email": "updated@example.test"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.learner.refresh_from_db()
        self.assertEqual(self.learner.email, "updated@example.test")
        response = self.client.patch(
            "/api/auth/profile/", {"email": self.teacher.email.upper()}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_administrative_service_rejects_non_admin_callers(self):
        from rest_framework.exceptions import PermissionDenied

        from accounts.services import administer_account

        with self.assertRaises(PermissionDenied):
            administer_account(
                administrator=self.teacher, user_id=self.learner.id, action="deactivate"
            )
        self.learner.refresh_from_db()
        self.assertEqual(self.learner.status, AccountStatus.ACTIVE)
