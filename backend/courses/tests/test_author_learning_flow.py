"""Exercise the real API boundary from author creation to learner certificate."""

from common.tests.factories import LearningTestCase


class AuthorLearningFlowTests(LearningTestCase):
    def test_published_lesson_course_can_be_completed(self):
        self.sign_in(self.teacher)
        response = self.client.post(
            "/api/author/courses/",
            {
                "subject": self.subject.id,
                "title": "A newly authored course",
                "description": "A clear introduction with a complete lesson.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        course_id = response.data["id"]
        self.assertEqual(response.data["teacher"], self.teacher.id)
        response = self.client.post(
            "/api/author/topics/",
            {"course": course_id, "title": "First topic"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        topic_id = response.data["id"]
        response = self.client.post(
            "/api/author/materials/",
            {
                "topic": topic_id,
                "title": "A complete first lesson",
                "kind": "Text",
                "text_content": "Read this explanation and practise what you learned.",
                "status": "Published",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        material_id = response.data["id"]
        response = self.client.patch(
            f"/api/author/courses/{course_id}/", {"status": "Published"}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)

        self.sign_in(self.learner)
        self.assertEqual(self.client.get(f"/api/materials/{material_id}/").status_code, 403)
        response = self.client.post(f"/api/courses/{course_id}/enrollment/")
        self.assertEqual(response.status_code, 201)
        response = self.client.get(f"/api/materials/{material_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["can_complete"])
        response = self.client.post(f"/api/materials/{material_id}/complete/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["percent"], 100)
        response = self.client.get(f"/api/courses/{course_id}/certificate/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["learner"], self.learner.full_name)
