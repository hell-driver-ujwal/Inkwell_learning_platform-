"""Closed discussions, author moderation and parent ownership checks."""

from activities.models import Activity
from common.tests.factories import LearningTestCase

from discussions.models import Post


class DiscussionTests(LearningTestCase):
    def setUp(self):
        super().setUp()
        self.discussion = Activity.objects.create(
            topic=self.topic,
            title="Discuss your learning",
            description="Share something useful you learned.",
            kind="Discussion",
            status="Published",
        )
        self.post = Post.objects.create(
            activity=self.discussion, user=self.learner, content="A useful contribution."
        )

    def test_admin_cannot_post_in_another_authors_course(self):
        self.sign_in(self.admin)
        response = self.client.post(
            "/api/posts/",
            {"activity": self.discussion.id, "content": "An admin contribution."},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_closed_discussion_blocks_edit_but_allows_moderation(self):
        self.discussion.is_closed = True
        self.discussion.save()
        self.sign_in(self.learner)
        self.assertEqual(
            self.client.patch(
                f"/api/posts/{self.post.id}/", {"content": "Changed content."}, format="json"
            ).status_code,
            403,
        )
        self.sign_in(self.teacher)
        self.assertEqual(self.client.delete(f"/api/posts/{self.post.id}/").status_code, 204)

    def test_reply_to_reply_rejected(self):
        reply = Post.objects.create(
            activity=self.discussion, user=self.learner, parent=self.post, content="First reply."
        )
        self.sign_in(self.learner)
        response = self.client.post(
            "/api/posts/",
            {"activity": self.discussion.id, "parent": reply.id, "content": "Nested reply."},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
