"""Activity metadata, learner play and private attempt history."""

from accounts.models import UserRole
from accounts.permissions import SessionReady
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from scenarios.services import move_scenario

from activities.models import Activity, Attempt
from activities.permissions import require_activity_access, require_attempt_access
from activities.selectors import play_content, run_payload
from activities.serializers import (
    ActivitySerializer,
    AttemptSerializer,
    ScenarioMoveSerializer,
    StartSerializer,
    SubmissionSerializer,
)
from activities.services import start_activity, submit_activity


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated, SessionReady]
    queryset = Activity.objects.select_related("topic__course")

    def list(self, request, *args, **kwargs):
        raise PermissionDenied("Open an activity from its course outline.")

    def retrieve(self, request, *args, **kwargs):
        activity = self.get_object()
        preview = request.query_params.get("preview") == "1"
        require_activity_access(user=request.user, activity=activity, preview=preview)
        return Response({**self.get_serializer(activity).data, **play_content(activity)})

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        serializer = StartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = start_activity(user=request.user, activity_id=pk, **serializer.validated_data)
        return Response(run_payload(run))

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            self.get_object().runs, pk=serializer.validated_data["run_id"], user=request.user
        )
        run = submit_activity(user=request.user, **serializer.validated_data)
        return Response(run_payload(run))

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        serializer = ScenarioMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            self.get_object().runs, pk=serializer.validated_data["run_id"], user=request.user
        )
        run = move_scenario(user=request.user, **serializer.validated_data)
        return Response(run_payload(run))


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated, SessionReady]
    filterset_fields = ["activity", "activity__topic__course"]

    def get_queryset(self):
        user = self.request.user
        attempts = Attempt.objects.select_related(
            "activity__topic__course", "learner", "ending_step"
        )
        if user.role == UserRole.ADMIN:
            return attempts
        if user.role == UserRole.TEACHER:
            return attempts.filter(activity__topic__course__teacher=user)
        return attempts.filter(learner=user)

    def retrieve(self, request, *args, **kwargs):
        attempt = self.get_object()
        require_attempt_access(user=request.user, attempt=attempt)
        result = self.get_serializer(attempt).data
        result["review"] = [
            {
                "text": answer.question.text,
                "selected_option": answer.selected_option_id,
                "options": list(answer.question.options.values("id", "text", "is_correct")),
            }
            for answer in attempt.quiz_answers.select_related("question")
        ]
        from activities.results import confidence_comparison

        result["ratings"] = list(attempt.ratings.values("statement__text", "rating"))
        result["confidence_comparison"] = confidence_comparison(attempt)
        result["ending_feedback"] = attempt.ending_step.feedback if attempt.ending_step else None
        return Response(result)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        from activities.results import summarize_attempts

        return Response(summarize_attempts(self.filter_queryset(self.get_queryset())))

    @action(detail=False, methods=["get"])
    def filters(self, request):
        attempts = self.get_queryset().order_by()
        return Response(
            {
                "courses": list(
                    attempts.values(
                        "activity__topic__course_id", "activity__topic__course__title"
                    ).distinct()
                ),
                "activities": list(
                    attempts.values(
                        "activity_id", "activity__title", "activity__topic__course_id"
                    ).distinct()
                ),
            }
        )
