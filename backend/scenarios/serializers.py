"""Scenario authoring uses local keys to connect steps in one atomic save."""

from rest_framework import serializers

from scenarios.models import Step


class StepInputSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=50)
    text = serializers.CharField(min_length=10, max_length=1000)
    is_ending = serializers.BooleanField(default=False)
    outcome = serializers.ChoiceField(choices=Step.Outcome.choices, allow_blank=True, default="")
    feedback = serializers.CharField(max_length=500, allow_blank=True, default="")


class ChoiceInputSerializer(serializers.Serializer):
    from_key = serializers.CharField()
    next_key = serializers.CharField()
    text = serializers.CharField(min_length=2, max_length=150)


class ScenarioContentSerializer(serializers.Serializer):
    start_key = serializers.CharField()
    steps = StepInputSerializer(many=True)
    choices = ChoiceInputSerializer(many=True)

    def validate(self, attrs):
        keys = [step["key"] for step in attrs["steps"]]
        if len(keys) != len(set(keys)) or attrs["start_key"] not in keys:
            raise serializers.ValidationError("Use unique step keys and an existing start key.")
        for choice in attrs["choices"]:
            if (
                choice["from_key"] not in keys
                or choice["next_key"] not in keys
                or choice["from_key"] == choice["next_key"]
            ):
                raise serializers.ValidationError("Choices must connect different existing steps.")
        return attrs


class StepImageSerializer(serializers.Serializer):
    """The uploaded image is tied to an existing, owned scenario step."""

    step_id = serializers.IntegerField(min_value=1)
    image = serializers.FileField(required=False)
    image_alt = serializers.CharField(
        min_length=5, max_length=150, required=False, allow_blank=True
    )
    remove = serializers.BooleanField(default=False)

    def validate(self, attrs):
        from courses.uploads import validate_upload

        if not attrs["remove"]:
            if not attrs.get("image") or not attrs.get("image_alt"):
                raise serializers.ValidationError("Provide an image and alternative text.")
            attrs["image"] = validate_upload(attrs["image"], "Image")
        return attrs
