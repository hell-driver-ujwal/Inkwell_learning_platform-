"""Payment receipts expose masked provider references, never full phone numbers."""

from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "course",
            "course_title",
            "transaction_uuid",
            "provider_reference",
            "amount_npr",
            "status",
            "created_at",
            "verified_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(min_value=1)


class VerificationSerializer(serializers.Serializer):
    phone = serializers.RegexField(r"^9[78][0-9]{8}$")
    code = serializers.RegexField(r"^[0-9]{4}$")
