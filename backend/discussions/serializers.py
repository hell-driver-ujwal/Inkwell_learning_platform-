"""Discussion post representations retain the author and parent relationship."""

from rest_framework import serializers

from discussions.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.full_name", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "activity",
            "user",
            "author",
            "role",
            "parent",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user"]
