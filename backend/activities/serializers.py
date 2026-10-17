"""Play inputs are explicit so unknown IDs and invalid ratings are rejected."""

from rest_framework import serializers

from activities.models import Activity, Attempt


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "id",
            "topic",
            "title",
            "description",
            "kind",
            "status",
            "sort_order",
            "time_limit_minutes",
            "max_attempts",
            "game_template",
            "is_closed",
            "start_step",
            "revision",
        ]
        read_only_fields = ["revision"]

    def validate(self, attrs):
        kind = attrs.get("kind", self.instance.kind if self.instance else None)
        if kind != Activity.Kind.QUIZ and (
            attrs.get("time_limit_minutes", 0) or attrs.get("max_attempts", 0)
        ):
            raise serializers.ValidationError("Only quizzes have time and attempt limits.")
        if kind != Activity.Kind.GAME and attrs.get("game_template"):
            raise serializers.ValidationError("Only games have a game template.")
        if kind != Activity.Kind.DISCUSSION and attrs.get("is_closed"):
            raise serializers.ValidationError("Only discussions can be closed.")
        step = attrs.get("start_step")
        if step and (
            kind != Activity.Kind.SCENARIO
            or not self.instance
            or step.activity_id != self.instance.pk
        ):
            raise serializers.ValidationError("Choose a start step from this scenario.")
        return attrs


class StartSerializer(serializers.Serializer):
    preview = serializers.BooleanField(default=False)


class QuizAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    option_id = serializers.IntegerField(min_value=1, allow_null=True, required=False)


class GameAnswerSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(min_value=1)
    value = serializers.CharField(max_length=200, allow_blank=True, trim_whitespace=False)


class RatingSerializer(serializers.Serializer):
    statement_id = serializers.IntegerField(min_value=1)
    rating = serializers.IntegerField(min_value=1, max_value=5)


class SubmissionSerializer(serializers.Serializer):
    run_id = serializers.UUIDField()
    answers = QuizAnswerSerializer(many=True, required=False)
    game_answers = GameAnswerSerializer(many=True, required=False)
    ratings = RatingSerializer(many=True, required=False)
    moves = serializers.IntegerField(min_value=1, required=False)


class ScenarioMoveSerializer(serializers.Serializer):
    run_id = serializers.UUIDField()
    step_version = serializers.IntegerField(min_value=0)
    choice_id = serializers.IntegerField(min_value=1, required=False)
    finish = serializers.BooleanField(default=False)


class AttemptSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source="activity.title", read_only=True)
    kind = serializers.CharField(source="activity.kind", read_only=True)
    learner_name = serializers.CharField(source="learner.full_name", read_only=True)
    outcome = serializers.CharField(source="ending_step.outcome", read_only=True, default=None)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "activity",
            "activity_title",
            "kind",
            "learner_name",
            "score_percent",
            "time_taken_seconds",
            "submitted_at",
            "outcome",
        ]
