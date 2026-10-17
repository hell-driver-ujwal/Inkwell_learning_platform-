"""Small explicit fixtures shared by business-rule tests."""

from accounts.models import User, UserRole
from activities.models import Activity
from courses.models import Course, Material, Subject, Topic
from django.test import TestCase
from learning.models import Enrollment
from quizzes.models import Option, Question
from rest_framework.test import APIClient


class LearningTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user(
            "teacher@example.test", "Learning123!", full_name="Course Author", role=UserRole.TEACHER
        )
        cls.other_teacher = User.objects.create_user(
            "other@example.test", "Learning123!", full_name="Other Author", role=UserRole.TEACHER
        )
        cls.admin = User.objects.create_user(
            "admin@example.test", "Learning123!", full_name="Administrator", role=UserRole.ADMIN
        )
        cls.learner = User.objects.create_user(
            "learner@example.test", "Learning123!", full_name="Learner One"
        )
        cls.other_learner = User.objects.create_user(
            "second@example.test", "Learning123!", full_name="Learner Two"
        )
        cls.subject = Subject.objects.create(name="Programming")
        cls.course = Course.objects.create(
            teacher=cls.teacher,
            subject=cls.subject,
            title="A readable course",
            description="A complete introduction to readable programming.",
            status="Published",
        )
        cls.topic = Topic.objects.create(course=cls.course, title="Getting started")
        cls.material = Material.objects.create(
            topic=cls.topic,
            title="First lesson",
            kind="Text",
            text_content="A lesson with enough useful text.",
            status="Published",
        )
        cls.quiz = Activity.objects.create(
            topic=cls.topic, kind="Quiz", title="First quiz", status="Published", max_attempts=1
        )
        cls.question = Question.objects.create(
            activity=cls.quiz, text="Which option is correct?", marks=3
        )
        cls.correct = Option.objects.create(
            question=cls.question, text="Correct answer", is_correct=True
        )
        cls.wrong = Option.objects.create(question=cls.question, text="Wrong answer")
        Enrollment.objects.create(learner=cls.learner, course=cls.course)

    def setUp(self):
        self.client = APIClient()

    def sign_in(self, user):
        self.client.force_authenticate(user)
