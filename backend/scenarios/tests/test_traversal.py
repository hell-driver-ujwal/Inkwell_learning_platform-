"""Branch ownership, stale-tab protection and atomic ending completion."""

from activities.models import Activity, Attempt
from activities.services import start_activity
from common.tests.factories import LearningTestCase
from rest_framework.exceptions import ValidationError

from scenarios.models import Choice, Step
from scenarios.services import move_scenario


class ScenarioTests(LearningTestCase):
    def setUp(self):
        super().setUp()
        self.scenario = Activity.objects.create(
            topic=self.topic,
            title="A difficult choice",
            description="Choose how to handle this situation.",
            kind="Scenario",
            status="Published",
        )
        self.start = Step.objects.create(
            activity=self.scenario, text="What would you do in this situation?"
        )
        self.middle = Step.objects.create(
            activity=self.scenario, text="Consider the evidence before deciding."
        )
        self.ending = Step.objects.create(
            activity=self.scenario,
            text="You reached a thoughtful conclusion.",
            is_ending=True,
            outcome="Best",
            feedback="You considered the evidence carefully.",
        )
        self.first_choice = Choice.objects.create(
            from_step=self.start, next_step=self.middle, text="Investigate first"
        )
        self.last_choice = Choice.objects.create(
            from_step=self.middle, next_step=self.ending, text="Make a decision"
        )
        self.scenario.start_step = self.start
        self.scenario.save()

    def test_cannot_jump_to_unreached_choice(self):
        run = start_activity(user=self.learner, activity_id=self.scenario.id)
        with self.assertRaises(ValidationError):
            move_scenario(
                user=self.learner, run_id=run.id, step_version=0, choice_id=self.last_choice.id
            )
        self.assertFalse(Attempt.objects.exists())

    def test_stale_step_version_is_rejected(self):
        run = start_activity(user=self.learner, activity_id=self.scenario.id)
        move_scenario(
            user=self.learner, run_id=run.id, step_version=0, choice_id=self.first_choice.id
        )
        with self.assertRaises(ValidationError):
            move_scenario(
                user=self.learner, run_id=run.id, step_version=0, choice_id=self.last_choice.id
            )

    def test_ending_creates_exactly_one_attempt(self):
        run = start_activity(user=self.learner, activity_id=self.scenario.id)
        move_scenario(
            user=self.learner, run_id=run.id, step_version=0, choice_id=self.first_choice.id
        )
        result = move_scenario(
            user=self.learner, run_id=run.id, step_version=1, choice_id=self.last_choice.id
        )
        move_scenario(
            user=self.learner, run_id=run.id, step_version=1, choice_id=self.last_choice.id
        )
        self.assertEqual(result.result["outcome"], "Best")
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(result.attempt.ending_step_id, self.ending.id)

    def test_preview_does_not_create_attempt(self):
        run = start_activity(user=self.teacher, activity_id=self.scenario.id, preview=True)
        move_scenario(
            user=self.teacher, run_id=run.id, step_version=0, choice_id=self.first_choice.id
        )
        move_scenario(
            user=self.teacher, run_id=run.id, step_version=1, choice_id=self.last_choice.id
        )
        self.assertFalse(Attempt.objects.exists())

    def test_editor_preserves_images_when_replacing_the_graph(self):
        from activities.author_views import author_content
        from activities.authoring import replace_content

        from scenarios.serializers import ScenarioContentSerializer

        self.start.image = "legacy/Images/example.png"
        self.start.image_alt = "Evidence on a desk"
        self.start.save()
        serializer = ScenarioContentSerializer(data=author_content(self.scenario))
        serializer.is_valid(raise_exception=True)
        updated = replace_content(
            user=self.teacher, activity_id=self.scenario.id, content=serializer.validated_data
        )
        self.assertEqual(updated.start_step.image.name, "legacy/Images/example.png")
        self.assertEqual(updated.start_step.image_alt, "Evidence on a desk")

    def test_image_removal_does_not_require_new_alternative_text(self):
        from scenarios.serializers import StepImageSerializer

        serializer = StepImageSerializer(
            data={"step_id": self.start.id, "remove": True, "image_alt": ""}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
