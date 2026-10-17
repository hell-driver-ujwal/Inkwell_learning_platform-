"""Owned course, topic and lesson CRUD for lecturers and admin authors."""

from accounts.permissions import IsAuthor, SessionReady
from learning.selectors import course_progress
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from courses.deletion import delete_course, delete_topic
from courses.models import Course, Material, Topic
from courses.permissions import require_owner
from courses.serializers import CourseWriteSerializer, MaterialWriteSerializer, TopicSerializer
from courses.services import save_course


class AuthorCourseViewSet(viewsets.ModelViewSet):
    permission_classes = [SessionReady, IsAuthor]
    serializer_class = CourseWriteSerializer

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user).select_related("teacher", "subject")

    def perform_create(self, serializer):
        save_course(user=self.request.user, serializer=serializer)

    def perform_update(self, serializer):
        save_course(user=self.request.user, serializer=serializer)

    def perform_destroy(self, instance):
        delete_course(user=self.request.user, course=instance)

    @action(detail=True, methods=["get"])
    def learners(self, request, pk=None):
        course = self.get_object()
        return Response(
            [
                {
                    "id": enrollment.learner_id,
                    "name": enrollment.learner.full_name,
                    "progress": course_progress(learner=enrollment.learner, course=course),
                }
                for enrollment in course.enrollments.select_related("learner")
            ]
        )


class AuthorTopicViewSet(viewsets.ModelViewSet):
    permission_classes = [SessionReady, IsAuthor]
    serializer_class = TopicSerializer
    filterset_fields = ["course"]

    def get_queryset(self):
        return Topic.objects.filter(course__teacher=self.request.user).select_related("course")

    def perform_create(self, serializer):
        require_owner(self.request.user, serializer.validated_data["course"])
        serializer.save()

    def perform_update(self, serializer):
        course = serializer.validated_data.get("course", serializer.instance.course)
        require_owner(self.request.user, course)
        if course != serializer.instance.course:
            raise ValidationError("Topics cannot move between courses.")
        serializer.save()

    def perform_destroy(self, instance):
        delete_topic(user=self.request.user, topic=instance)


class AuthorMaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [SessionReady, IsAuthor]
    serializer_class = MaterialWriteSerializer
    filterset_fields = ["topic"]

    def get_queryset(self):
        return Material.objects.filter(topic__course__teacher=self.request.user).select_related(
            "topic__course"
        )

    def perform_create(self, serializer):
        require_owner(self.request.user, serializer.validated_data["topic"].course)
        serializer.save()

    def perform_update(self, serializer):
        topic = serializer.validated_data.get("topic", serializer.instance.topic)
        require_owner(self.request.user, topic.course)
        if topic != serializer.instance.topic:
            raise ValidationError("Lessons cannot move between topics.")
        serializer.save()
