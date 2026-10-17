"""Crawler discovery includes public introductions and excludes draft courses."""

from common.tests.factories import LearningTestCase


class DiscoveryTests(LearningTestCase):
    def test_only_published_courses_appear_in_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertContains(response, f"/courses/{self.course.id}</loc>")
        self.course.status = "Draft"
        self.course.save()
        response = self.client.get("/sitemap.xml")
        self.assertNotContains(response, f"/courses/{self.course.id}</loc>")

    def test_robots_excludes_private_routes(self):
        self.assertContains(self.client.get("/robots.txt"), "Disallow: /api/")
