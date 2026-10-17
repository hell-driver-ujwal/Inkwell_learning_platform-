"""Verified payments and enrollment must commit as one business action."""

from common.tests.factories import LearningTestCase
from learning.models import Enrollment
from learning.services import enroll_learner, leave_course
from rest_framework.exceptions import ValidationError

from payments.models import Payment
from payments.services import begin_payment, cancel_payment, complete_payment


class PaymentTests(LearningTestCase):
    def setUp(self):
        super().setUp()
        self.course.is_paid = True
        self.course.price_npr = 499
        self.course.save()

    def test_price_comes_from_course_and_completion_is_idempotent(self):
        payment = begin_payment(learner=self.other_learner, course_id=self.course.id)
        self.assertEqual(payment.amount_npr, 499)
        first = complete_payment(
            learner=self.other_learner, payment_id=payment.id, phone="9841234567", code="4567"
        )
        second = complete_payment(
            learner=self.other_learner, payment_id=payment.id, phone="9841234567", code="4567"
        )
        self.assertEqual(first.provider_reference, second.provider_reference)
        self.assertEqual(Enrollment.objects.filter(learner=self.other_learner).count(), 1)
        self.assertNotIn("9841234567", first.provider_reference)

    def test_three_wrong_codes_persist_failure(self):
        payment = begin_payment(learner=self.other_learner, course_id=self.course.id)
        for _ in range(3):
            with self.assertRaises(ValidationError):
                complete_payment(
                    learner=self.other_learner,
                    payment_id=payment.id,
                    phone="9841234567",
                    code="0000",
                )
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.FAILED)
        self.assertFalse(Enrollment.objects.filter(learner=self.other_learner).exists())

    def test_cancel_does_not_reverse_completed_payment(self):
        payment = begin_payment(learner=self.other_learner, course_id=self.course.id)
        complete_payment(
            learner=self.other_learner, payment_id=payment.id, phone="9841234567", code="4567"
        )
        cancel_payment(learner=self.other_learner, payment_id=payment.id)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.COMPLETE)

    def test_reenroll_after_leaving_does_not_need_second_payment(self):
        payment = begin_payment(learner=self.other_learner, course_id=self.course.id)
        complete_payment(
            learner=self.other_learner, payment_id=payment.id, phone="9841234567", code="4567"
        )
        leave_course(learner=self.other_learner, course=self.course)
        enroll_learner(learner=self.other_learner, course=self.course)
        self.assertEqual(Payment.objects.count(), 1)

    def test_receipt_cannot_be_read_by_another_learner(self):
        payment = begin_payment(learner=self.other_learner, course_id=self.course.id)
        self.sign_in(self.learner)
        self.assertEqual(self.client.get(f"/api/payments/{payment.id}/").status_code, 404)
