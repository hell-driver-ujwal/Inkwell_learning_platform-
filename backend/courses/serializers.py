"""Catalogue output excludes lesson bodies; author inputs validate content requirements."""

import re
from urllib.parse import parse_qs, urlparse

from rest_framework import serializers

from courses.models import Course, Material, Subject, Topic
from courses.uploads import validate_upload


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "description"]


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "subject",
            "subject_name",
            "title",
            "description",
            "status",
            "is_paid",
            "price_npr",
            "cover_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["teacher"]

    def get_cover_url(self, course):
        return f"/api/courses/{course.pk}/cover/" if course.cover else None

    def validate(self, attrs):
        paid = attrs.get("is_paid", self.instance.is_paid if self.instance else False)
        price = attrs.get("price_npr", self.instance.price_npr if self.instance else 0)
        if (paid and price <= 0) or (not paid and price != 0):
            raise serializers.ValidationError(
                {"price_npr": "Paid courses need a positive price; free courses must cost zero."}
            )
        return attrs


class CourseWriteSerializer(CourseSerializer):
    cover = serializers.FileField(required=False, write_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ["cover"]

    def validate_cover(self, value):
        return validate_upload(value, "Image", cover=True)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "course", "title", "sort_order"]


class MaterialSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    captions_url = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="topic.course_id", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id",
            "topic",
            "course_id",
            "title",
            "kind",
            "status",
            "text_content",
            "file_url",
            "captions_url",
            "youtube_url",
            "alt_text",
            "is_preview",
            "sort_order",
        ]

    def get_captions_url(self, material):
        from pathlib import Path

        if (
            material.kind == Material.Kind.VIDEO
            and material.file
            and Path(material.file.path).with_suffix(".vtt").is_file()
        ):
            return f"/api/materials/{material.pk}/captions/"
        return None

    def get_file_url(self, material):
        return f"/api/materials/{material.pk}/file/" if material.file else None


class MaterialWriteSerializer(MaterialSerializer):
    file = serializers.FileField(required=False, write_only=True)

    class Meta(MaterialSerializer.Meta):
        fields = MaterialSerializer.Meta.fields + ["file"]

    def validate(self, attrs):
        def value(field, default=""):
            return attrs.get(field, getattr(self.instance, field, default))

        kind = value("kind")
        if "file" in attrs:
            attrs["file"] = validate_upload(attrs["file"], kind)
        if kind in (Material.Kind.TEXT, Material.Kind.CODE) and len(value("text_content")) < 20:
            raise serializers.ValidationError({"text_content": "Enter at least 20 characters."})
        if kind == Material.Kind.IMAGE and len(value("alt_text")) < 5:
            raise serializers.ValidationError(
                {"alt_text": "Describe the image in at least five characters."}
            )
        if kind in (
            Material.Kind.IMAGE,
            Material.Kind.PDF,
            Material.Kind.VIDEO,
            Material.Kind.AUDIO,
        ) and not value("file"):
            raise serializers.ValidationError({"file": "Upload a file for this lesson."})
        if kind == Material.Kind.YOUTUBE:
            parsed = urlparse(value("youtube_url"))
            video_id = (
                parse_qs(parsed.query).get("v", [""])[0]
                if parsed.path == "/watch"
                else parsed.path.lstrip("/")
            )
            if (
                parsed.scheme not in ("http", "https")
                or parsed.netloc
                not in ("youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be")
                or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id)
            ):
                raise serializers.ValidationError(
                    {"youtube_url": "Use a valid YouTube watch or youtu.be URL."}
                )
        return attrs
