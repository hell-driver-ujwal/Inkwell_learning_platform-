"""Self-assessment authoring fields."""

from rest_framework import serializers

from assessments.models import Statement


class StatementSerializer(serializers.ModelSerializer):
    text = serializers.CharField(min_length=5, max_length=200)

    class Meta:
        model = Statement
        fields = ["id", "text", "sort_order"]
