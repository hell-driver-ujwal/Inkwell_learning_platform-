"""Administrator FAQ, subject, message, receipt and unpublishing oversight."""

from accounts.permissions import IsAdmin, SessionReady
from activities.models import Activity
from activities.serializers import ActivitySerializer
from courses.models import Course, Subject
from courses.serializers import CourseSerializer, SubjectSerializer
from payments.models import Payment
from payments.serializers import PaymentSerializer
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from support.models import FAQ, ContactMessage
from support.serializers import FAQSerializer, MessageSerializer


class AdminSubjectViewSet(viewsets.ModelViewSet):
    permission_classes = [SessionReady, IsAdmin]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class AdminFAQViewSet(viewsets.ModelViewSet):
    permission_classes = [SessionReady, IsAdmin]
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class AdminMessageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SessionReady, IsAdmin]
    queryset = ContactMessage.objects.order_by("-created_at")
    serializer_class = MessageSerializer

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=["is_read"])
        return Response(self.get_serializer(message).data)


class AdminPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SessionReady, IsAdmin]
    queryset = Payment.objects.select_related("course")
    serializer_class = PaymentSerializer
    filterset_fields = ["status"]


class AdminCourseViewSet(mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [SessionReady, IsAdmin]
    queryset = Course.objects.select_related("teacher", "subject")
    serializer_class = CourseSerializer

    def perform_destroy(self, instance):
        from courses.deletion import delete_course

        delete_course(user=self.request.user, course=instance)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.status = "Draft"
        course.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(course).data)


class AdminActivityViewSet(mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [SessionReady, IsAdmin]
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def perform_destroy(self, instance):
        from courses.deletion import delete_activity

        delete_activity(user=self.request.user, activity=instance)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        activity = self.get_object()
        activity.status = "Draft"
        activity.save(update_fields=["status"])
        return Response(self.get_serializer(activity).data)
