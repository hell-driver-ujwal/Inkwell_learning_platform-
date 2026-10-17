"""API entry points: public resources, learner actions and explicit author/admin namespaces."""

from accounts.views import UserAdminViewSet
from activities.author_views import AuthorActivityViewSet
from activities.views import ActivityViewSet, AttemptViewSet
from analytics.views import AnalyticsView, DashboardView, PageViewEndpoint
from courses.author_views import AuthorCourseViewSet, AuthorMaterialViewSet, AuthorTopicViewSet
from courses.views import CourseViewSet, MaterialViewSet, SubjectViewSet
from discussions.views import PostViewSet
from django.contrib import admin
from django.urls import include, path
from learning.views import (
    BookmarksView,
    BookmarkView,
    CertificateView,
    CompletionView,
    EnrollmentView,
    MyCoursesView,
    ReviewView,
)
from payments.views import PaymentViewSet
from rest_framework.routers import DefaultRouter
from scenarios.views import ScenarioImageView
from support.admin_views import (
    AdminActivityViewSet,
    AdminCourseViewSet,
    AdminFAQViewSet,
    AdminMessageViewSet,
    AdminPaymentViewSet,
    AdminSubjectViewSet,
)
from support.seo import robots, sitemap
from support.views import CaptchaView, ContactView, FAQViewSet

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="course")
router.register("subjects", SubjectViewSet)
router.register("materials", MaterialViewSet)
router.register("activities", ActivityViewSet)
router.register("attempts", AttemptViewSet, basename="attempt")
router.register("posts", PostViewSet, basename="post")
router.register("payments", PaymentViewSet, basename="payment")
router.register("faqs", FAQViewSet, basename="faq")
router.register("author/courses", AuthorCourseViewSet, basename="author-course")
router.register("author/topics", AuthorTopicViewSet, basename="author-topic")
router.register("author/materials", AuthorMaterialViewSet, basename="author-material")
router.register("author/activities", AuthorActivityViewSet, basename="author-activity")
router.register("admin/users", UserAdminViewSet, basename="admin-user")
router.register("admin/subjects", AdminSubjectViewSet, basename="admin-subject")
router.register("admin/faqs", AdminFAQViewSet, basename="admin-faq")
router.register("admin/messages", AdminMessageViewSet, basename="admin-message")
router.register("admin/payments", AdminPaymentViewSet, basename="admin-payment")
router.register("admin/courses", AdminCourseViewSet, basename="admin-course")
router.register("admin/activities", AdminActivityViewSet, basename="admin-activity")
urlpatterns = [
    path("robots.txt", robots),
    path("sitemap.xml", sitemap),
    path("django-admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include(router.urls)),
    path("api/dashboard/", DashboardView.as_view()),
    path("api/my-courses/", MyCoursesView.as_view()),
    path("api/bookmarks/", BookmarksView.as_view()),
    path("api/courses/<int:course_id>/enrollment/", EnrollmentView.as_view()),
    path("api/courses/<int:course_id>/review/", ReviewView.as_view()),
    path("api/courses/<int:course_id>/certificate/", CertificateView.as_view()),
    path("api/materials/<int:material_id>/complete/", CompletionView.as_view()),
    path("api/materials/<int:material_id>/bookmark/", BookmarkView.as_view()),
    path("api/scenario-images/<int:step_id>/", ScenarioImageView.as_view()),
    path("api/contact/", ContactView.as_view()),
    path("api/captcha/", CaptchaView.as_view()),
    path("api/page-views/", PageViewEndpoint.as_view()),
    path("api/admin/analytics/", AnalyticsView.as_view()),
]
