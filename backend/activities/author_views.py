"""Course-owner APIs for metadata and domain-specific content editors."""

from accounts.permissions import IsAuthor, SessionReady
from assessments.serializers import StatementSerializer
from games.serializers import GameContentSerializer
from quizzes.serializers import QuestionSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from scenarios.serializers import ScenarioContentSerializer

from activities.authoring import replace_content, save_activity
from activities.models import Activity
from activities.serializers import ActivitySerializer


class AuthorActivityViewSet(viewsets.ModelViewSet):
    permission_classes = [SessionReady, IsAuthor]
    serializer_class = ActivitySerializer
    filterset_fields = ["topic"]

    def get_queryset(self):
        return Activity.objects.filter(topic__course__teacher=self.request.user).select_related(
            "topic__course"
        )

    def perform_create(self, serializer):
        save_activity(user=self.request.user, serializer=serializer)

    def perform_update(self, serializer):
        save_activity(user=self.request.user, serializer=serializer)

    def perform_destroy(self, instance):
        from courses.deletion import delete_activity

        delete_activity(user=self.request.user, activity=instance)

    @action(detail=True, methods=["get", "put"])
    def content(self, request, pk=None):
        activity = self.get_object()
        if request.method == "GET":
            return Response(author_content(activity))
        if activity.kind == Activity.Kind.QUIZ:
            serializer = QuestionSerializer(data=request.data, many=True)
        elif activity.kind == Activity.Kind.ASSESSMENT:
            serializer = StatementSerializer(data=request.data, many=True)
        elif activity.kind == Activity.Kind.GAME:
            serializer = GameContentSerializer(data=request.data)
        else:
            serializer = ScenarioContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = replace_content(
            user=request.user, activity_id=activity.id, content=serializer.validated_data
        )
        return Response(author_content(activity))

    @action(detail=True, methods=["post"], url_path="step-image")
    def step_image(self, request, pk=None):
        from scenarios.serializers import StepImageSerializer
        from scenarios.services import save_step_image

        activity = self.get_object()
        serializer = StepImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        save_step_image(user=request.user, activity_id=activity.id, **serializer.validated_data)
        return Response({"saved": True})


def author_content(activity):
    """Editor data includes answer keys and is only called after owner authorization."""
    if activity.kind == Activity.Kind.QUIZ:
        return QuestionSerializer(activity.questions.all(), many=True).data
    if activity.kind == Activity.Kind.ASSESSMENT:
        return StatementSerializer(activity.statements.all(), many=True).data
    if activity.kind == Activity.Kind.GAME:
        return {
            "groups": [
                {"key": str(group.id), "name": group.name} for group in activity.game_groups.all()
            ],
            "items": [
                {
                    "text": item.text,
                    "match_text": item.match_text,
                    "group_key": str(item.group_id) if item.group_id else "",
                }
                for item in activity.game_items.all()
            ],
        }
    return {
        "start_key": str(activity.start_step_id or ""),
        "steps": [
            {
                "key": str(step.id),
                "image_url": f"/api/scenario-images/{step.id}/" if step.image else None,
                "image_alt": step.image_alt,
                "text": step.text,
                "is_ending": step.is_ending,
                "outcome": step.outcome,
                "feedback": step.feedback,
            }
            for step in activity.steps.all()
        ],
        "choices": [
            {
                "from_key": str(choice.from_step_id),
                "next_key": str(choice.next_step_id),
                "text": choice.text,
            }
            for step in activity.steps.all()
            for choice in step.choices.all()
        ],
    }
