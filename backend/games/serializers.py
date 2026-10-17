"""Explicit authoring fields for game items and groups."""

from rest_framework import serializers


class GameGroupInputSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)


class GameItemInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=100)
    match_text = serializers.CharField(max_length=200, allow_blank=True, default="")
    group_key = serializers.CharField(required=False, allow_blank=True)


class GameContentSerializer(serializers.Serializer):
    groups = GameGroupInputSerializer(many=True)
    items = GameItemInputSerializer(many=True)

    def validate(self, attrs):
        names = [group["name"].casefold() for group in attrs["groups"]]
        if len(names) != len(set(names)):
            raise serializers.ValidationError("Group names must be distinct.")
        keys = [group["key"] for group in attrs["groups"]]
        if len(keys) != len(set(keys)):
            raise serializers.ValidationError("Group keys must be unique.")
        for item in attrs["items"]:
            if item.get("group_key") and item["group_key"] not in keys:
                raise serializers.ValidationError("An item refers to an unknown group.")
        return attrs
