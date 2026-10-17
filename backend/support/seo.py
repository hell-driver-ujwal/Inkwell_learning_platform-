"""Public crawler discovery without exposing private learning URLs."""

from xml.etree.ElementTree import Element, SubElement, tostring

from common.models import PublicationStatus
from courses.models import Course, Subject
from django.conf import settings
from django.http import HttpResponse


def robots(request):
    """Crawler exclusions are guidance; backend authorization still protects data."""
    private_paths = [
        "/api/",
        "/django-admin/",
        "/admin/",
        "/author/",
        "/dashboard",
        "/lessons/",
        "/activities/",
        "/results",
        "/payments",
        "/profile",
        "/password",
        "/bookmarks",
        "/my-courses",
        "/login",
    ]
    lines = ["User-agent: *", "Allow: /"]
    lines.extend(f"Disallow: {path}" for path in private_paths)
    lines.append(f"Sitemap: {settings.PUBLIC_SITE_URL}/sitemap.xml")
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap(request):
    """List static public pages, subjects and published course introductions."""
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    public_paths = [
        "",
        "courses",
        "about",
        "help",
        "contact",
        "sitemap",
        "privacy",
        "terms",
        "register",
    ]
    for path in public_paths:
        add_sitemap_url(root, f"/{path}")
    for subject_id in Subject.objects.values_list("id", flat=True):
        add_sitemap_url(root, f"/courses?subject={subject_id}")
    for course in Course.objects.filter(status=PublicationStatus.PUBLISHED).only(
        "id", "updated_at"
    ):
        add_sitemap_url(root, f"/courses/{course.id}", course.updated_at.date().isoformat())
    return HttpResponse(
        tostring(root, encoding="utf-8", xml_declaration=True), content_type="application/xml"
    )


def add_sitemap_url(root, path, last_modified=None):
    """ElementTree escapes URLs, including query parameters, for XML output."""
    entry = SubElement(root, "url")
    SubElement(entry, "loc").text = settings.PUBLIC_SITE_URL + path
    if last_modified:
        SubElement(entry, "lastmod").text = last_modified
