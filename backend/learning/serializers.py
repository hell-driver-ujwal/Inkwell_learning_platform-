"""Learner engagement representations."""

from rest_framework import serializers

from learning.models import Bookmark, Review


class ReviewSerializer(serializers.ModelSerializer):
    learner_name = serializers.CharField(source="learner.full_name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "learner", "learner_name", "rating", "comment", "created_at"]
        read_only_fields = ["learner"]


class BookmarkSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="material.title", read_only=True)
    course_title = serializers.CharField(source="material.topic.course.title", read_only=True)

    class Meta:
        model = Bookmark
        fields = ["id", "material", "title", "course_title", "created_at"]
