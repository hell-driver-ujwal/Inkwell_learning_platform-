"""Authoring serializers are separate from the learner's safe question payload."""

from rest_framework import serializers

from quizzes.models import Option, Question


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "marks", "sort_order", "options"]

    def validate_options(self, value):
        texts = [option["text"].casefold() for option in value]
        if len(texts) != len(set(texts)):
            raise serializers.ValidationError("Options must be distinct.")
        return value
