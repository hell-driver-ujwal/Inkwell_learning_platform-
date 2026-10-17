"""Public catalogue and authorized lesson reading endpoints."""

from accounts.permissions import SessionReady
from learning.selectors import course_progress
from learning.serializers import ReviewSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from courses.media import caption_response, protected_file_response
from courses.models import Material, Subject
from courses.permissions import can_preview, can_read_material, can_study
from courses.selectors import curriculum, visible_courses
from courses.serializers import CourseSerializer, MaterialSerializer, SubjectSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [SessionReady]
    search_fields = ["title", "description", "teacher__full_name"]
    filterset_fields = ["subject", "is_paid"]

    def get_queryset(self):
        return visible_courses(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        data = self.get_serializer(course).data
        data["topics"] = curriculum(user=request.user, course=course)
        data["can_study"] = can_study(request.user, course)
        data["can_preview"] = can_preview(request.user, course)
        data["reviews"] = ReviewSerializer(course.reviews.select_related("learner"), many=True).data
        if data["can_study"]:
            data["progress"] = course_progress(learner=request.user, course=course)
        return Response(data)

    @action(detail=True, methods=["get"])
    def cover(self, request, pk=None):
        return protected_file_response(self.get_object().cover, request)


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [SessionReady]
    queryset = Material.objects.select_related("topic__course")

    def list(self, request, *args, **kwargs):
        raise PermissionDenied("Open lessons from a course outline.")

    def get_object(self):
        material = super().get_object()
        if not can_read_material(self.request.user, material):
            raise PermissionDenied("This lesson requires enrollment or author preview access.")
        return material

    def retrieve(self, request, *args, **kwargs):
        from learning.models import Bookmark, Completion

        material = self.get_object()
        data = self.get_serializer(material).data
        data["can_complete"] = can_study(request.user, material.course)
        data["completed"] = (
            request.user.is_authenticated
            and Completion.objects.filter(learner=request.user, material=material).exists()
        )
        data["bookmarked"] = (
            request.user.is_authenticated
            and Bookmark.objects.filter(learner=request.user, material=material).exists()
        )
        return Response(data)

    @action(detail=True, methods=["get"], url_path="file")
    def download(self, request, pk=None):
        return protected_file_response(self.get_object().file, request)

    @action(detail=True, methods=["get"])
    def captions(self, request, pk=None):
        return caption_response(self.get_object())
