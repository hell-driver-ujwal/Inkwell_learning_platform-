"""Enrollment, progress, bookmarks, reviews and certificate endpoints."""

from accounts.permissions import IsLearner, SessionReady
from common.models import PublicationStatus
from courses.models import Course, Material
from courses.permissions import require_study
from courses.serializers import CourseSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from learning.models import Bookmark, Review
from learning.selectors import course_progress
from learning.serializers import BookmarkSerializer, ReviewSerializer
from learning.services import complete_material, enroll_learner, leave_course


class EnrollmentView(APIView):
    permission_classes = [SessionReady, IsLearner]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        enrollment = enroll_learner(learner=request.user, course=course)
        return Response({"id": enrollment.id}, status=status.HTTP_201_CREATED)

    def delete(self, request, course_id):
        leave_course(learner=request.user, course=get_object_or_404(Course, pk=course_id))
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyCoursesView(generics.ListAPIView):
    permission_classes = [SessionReady, IsLearner]
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(enrollments__learner=self.request.user).select_related(
            "teacher", "subject"
        )


class CompletionView(APIView):
    permission_classes = [SessionReady, IsLearner]

    def post(self, request, material_id):
        material = get_object_or_404(
            Material.objects.select_related("topic__course"), pk=material_id
        )
        complete_material(learner=request.user, material=material)
        return Response(course_progress(learner=request.user, course=material.course))


class BookmarksView(generics.ListAPIView):
    permission_classes = [SessionReady, IsLearner]
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return (
            Bookmark.objects.filter(learner=self.request.user)
            .select_related("material__topic__course")
            .order_by("-created_at")
        )


class BookmarkView(APIView):
    permission_classes = [SessionReady, IsLearner]

    def post(self, request, material_id):
        material = get_object_or_404(Material, pk=material_id, status=PublicationStatus.PUBLISHED)
        require_study(request.user, material.course)
        bookmark, _ = Bookmark.objects.get_or_create(learner=request.user, material=material)
        return Response(BookmarkSerializer(bookmark).data)

    def delete(self, request, material_id):
        Bookmark.objects.filter(learner=request.user, material_id=material_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewView(APIView):
    permission_classes = [SessionReady, IsLearner]

    def put(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        require_study(request.user, course)
        review = Review.objects.filter(learner=request.user, course=course).first()
        serializer = ReviewSerializer(review, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(learner=request.user, course=course)
        return Response(serializer.data)

    def delete(self, request, course_id):
        Review.objects.filter(learner=request.user, course_id=course_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CertificateView(APIView):
    permission_classes = [SessionReady, IsLearner]

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        require_study(request.user, course)
        progress = course_progress(learner=request.user, course=course)
        if progress["percent"] != 100:
            raise PermissionDenied("Complete every published item to earn a certificate.")
        return Response(
            {
                "learner": request.user.full_name,
                "course": course.title,
                "teacher": course.teacher.full_name,
                "certificate_id": f"INK-{course.id}-{request.user.id}",
            }
        )
