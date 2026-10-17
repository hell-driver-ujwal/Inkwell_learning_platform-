"""Deleting unused content is allowed; historical attempts and receipts block it."""

from activities.models import Activity, Attempt
from common.tests.factories import LearningTestCase
from discussions.models import Post
from games.models import Group, Item
from payments.models import Payment
from rest_framework.exceptions import ValidationError
from scenarios.models import Choice, Step

from courses.deletion import delete_activity, delete_course, delete_topic
from courses.models import Course


class DeletionTests(LearningTestCase):
    def test_delete_discussion_removes_posts_and_replies(self):
        discussion = Activity.objects.create(
            topic=self.topic, kind="Discussion", title="Discussion prompt"
        )
        parent = Post.objects.create(
            activity=discussion, user=self.learner, content="A thoughtful response"
        )
        Post.objects.create(
            activity=discussion, user=self.teacher, parent=parent, content="A useful reply"
        )
        delete_activity(user=self.admin, activity=discussion)
        self.assertFalse(Post.objects.exists())

    def test_delete_game_handles_protected_group_references(self):
        game = Activity.objects.create(
            topic=self.topic, kind="Game", title="Sorting game", game_template="Sort"
        )
        group = Group.objects.create(activity=game, name="First group")
        Item.objects.create(activity=game, group=group, text="First item")
        delete_activity(user=self.teacher, activity=game)
        self.assertFalse(Group.objects.exists())

    def test_delete_scenario_handles_graph_references(self):
        scenario = Activity.objects.create(
            topic=self.topic, kind="Scenario", title="A branching scenario"
        )
        first = Step.objects.create(activity=scenario, text="The initial situation")
        last = Step.objects.create(
            activity=scenario, text="The final outcome", is_ending=True, outcome="Best"
        )
        Choice.objects.create(from_step=first, next_step=last, text="Continue")
        scenario.start_step = first
        scenario.save()
        delete_activity(user=self.teacher, activity=scenario)
        self.assertFalse(Step.objects.exists())

    def test_topic_delete_rolls_back_when_an_activity_has_attempts(self):
        Attempt.objects.create(activity=self.quiz, learner=self.learner)
        with self.assertRaises(ValidationError):
            delete_topic(user=self.teacher, topic=self.topic)
        self.assertTrue(self.course.topics.exists())
        self.assertTrue(self.topic.materials.exists())

    def test_course_receipts_block_deletion(self):
        Payment.objects.create(course=self.course, learner=self.learner, amount_npr=10)
        with self.assertRaises(ValidationError):
            delete_course(user=self.admin, course=self.course)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())
