"""Public account representations and validated account inputs."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import AccountStatus, User, UserRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "status", "must_change_password"]
        read_only_fields = ["id", "role", "status", "must_change_password", "email"]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=[UserRole.LEARNER, UserRole.TEACHER])

    class Meta:
        model = User
        fields = ["email", "full_name", "password", "role", "application_reason"]
        extra_kwargs = {"full_name": {"min_length": 2}}

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account already uses this email.")
        return value.lower()

    def validate(self, attrs):
        if attrs["role"] == UserRole.TEACHER and len(attrs.get("application_reason", "")) < 20:
            raise serializers.ValidationError(
                {"application_reason": "Explain why you want to teach in at least 20 characters."}
            )
        return attrs

    def create(self, validated_data):
        status = (
            AccountStatus.PENDING
            if validated_data["role"] == UserRole.TEACHER
            else AccountStatus.ACTIVE
        )
        return User.objects.create_user(status=status, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserRole.choices)


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class AccountActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["approve", "reject", "activate", "deactivate", "unlock", "reset_password"]
    )
    password = serializers.CharField(
        required=False, write_only=True, validators=[validate_password]
    )

    def validate(self, attrs):
        if attrs["action"] == "reset_password" and not attrs.get("password"):
            raise serializers.ValidationError({"password": "A temporary password is required."})
        return attrs


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin-created accounts get a temporary password and cannot become admins."""

    password = serializers.CharField(
        write_only=True, required=False, validators=[validate_password]
    )
    role = serializers.ChoiceField(choices=[UserRole.LEARNER, UserRole.TEACHER])

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "status",
            "application_reason",
            "must_change_password",
            "password",
        ]
        read_only_fields = ["must_change_password"]

    def validate_email(self, value):
        matches = User.objects.filter(email__iexact=value)
        if self.instance:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise serializers.ValidationError("An account already uses this email.")
        return value.lower()

    def validate(self, attrs):
        if self.instance and self.instance.role == UserRole.ADMIN:
            raise serializers.ValidationError("Administrator accounts cannot be edited here.")
        if self.instance and attrs.get("role", self.instance.role) != self.instance.role:
            raise serializers.ValidationError(
                "Existing roles cannot change because learning history depends on them."
            )
        if not self.instance and not attrs.get("password"):
            raise serializers.ValidationError({"password": "A temporary password is required."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(must_change_password=True, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
            instance.must_change_password = True
        return super().update(instance, validated_data)


class ProfileSerializer(UserSerializer):
    """Profile editing preserves case-insensitive email uniqueness."""

    email = serializers.EmailField()
    full_name = serializers.CharField(min_length=2, max_length=100)

    class Meta(UserSerializer.Meta):
        read_only_fields = ["id", "role", "status", "must_change_password"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("An account already uses this email.")
        return value.lower()


class AdminUserDetailSerializer(UserSerializer):
    """Applications and lockout state are visible only in the admin namespace."""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            "application_reason",
            "failed_login_count",
            "locked_until",
        ]
