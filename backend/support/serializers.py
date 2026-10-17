"""Validate public contact and FAQ content."""

from rest_framework import serializers

from support.models import FAQ, ContactMessage


class FAQSerializer(serializers.ModelSerializer):
    question = serializers.CharField(min_length=5, max_length=200)
    answer = serializers.CharField(min_length=10, max_length=2000)

    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "audience", "sort_order"]


class ContactSerializer(serializers.ModelSerializer):
    captcha = serializers.IntegerField(write_only=True)
    sender_name = serializers.CharField(min_length=2, max_length=100)
    subject = serializers.CharField(min_length=3, max_length=100)
    message = serializers.CharField(min_length=10, max_length=2000)

    class Meta:
        model = ContactMessage
        fields = ["id", "sender_name", "sender_email", "subject", "message", "captcha"]

    def validate_captcha(self, value):
        expected = self.context["request"].session.pop("contact_captcha", None)
        if expected is None or value != expected:
            raise serializers.ValidationError("Incorrect or expired answer. Load a new question.")
        return value

    def create(self, validated_data):
        validated_data.pop("captcha")
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "sender_name",
            "sender_email",
            "subject",
            "message",
            "created_at",
            "is_read",
        ]
        read_only_fields = ["sender_name", "sender_email", "subject", "message", "created_at"]
