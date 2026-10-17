"""Scenario images follow the same activity access rules as scenario play."""

from accounts.permissions import SessionReady
from activities.permissions import require_activity_access
from courses.media import protected_file_response
from courses.permissions import can_preview
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from scenarios.models import Step


class ScenarioImageView(APIView):
    permission_classes = [IsAuthenticated, SessionReady]

    def get(self, request, step_id):
        step = get_object_or_404(Step.objects.select_related("activity__topic__course"), pk=step_id)
        require_activity_access(
            user=request.user,
            activity=step.activity,
            preview=can_preview(request.user, step.activity.course),
        )
        return protected_file_response(step.image, request)
