"""Import the reviewed, portable demo dataset into an empty PostgreSQL database."""

import json
import shutil
from pathlib import Path

from accounts.models import User
from activities.models import Activity
from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction

# Explicit mappings make the old-to-new schema easy to study and audit.
TABLES = [
    (
        "User",
        "accounts.User",
        {
            "UserID": "id",
            "FullName": "full_name",
            "Email": "email",
            "Role": "role",
            "Status": "status",
            "ApplicationReason": "application_reason",
            "CreatedDate": "date_joined",
        },
    ),
    (
        "Subject",
        "courses.Subject",
        {"SubjectID": "id", "SubjectName": "name", "Description": "description"},
    ),
    (
        "Course",
        "courses.Course",
        {
            "CourseID": "id",
            "TeacherID": "teacher_id",
            "SubjectID": "subject_id",
            "Title": "title",
            "Description": "description",
            "CoverImagePath": "cover",
            "Status": "status",
            "IsPaid": "is_paid",
            "PriceNPR": "price_npr",
            "CreatedDate": "created_at",
            "LastUpdated": "updated_at",
        },
    ),
    (
        "Topic",
        "courses.Topic",
        {"TopicID": "id", "CourseID": "course_id", "Title": "title", "SortOrder": "sort_order"},
    ),
    (
        "Material",
        "courses.Material",
        {
            "MaterialID": "id",
            "TopicID": "topic_id",
            "Title": "title",
            "MaterialType": "kind",
            "Status": "status",
            "TextContent": "text_content",
            "FilePath": "file",
            "YouTubeURL": "youtube_url",
            "AltText": "alt_text",
            "IsPreview": "is_preview",
            "SortOrder": "sort_order",
        },
    ),
    (
        "Activity",
        "activities.Activity",
        {
            "ActivityID": "id",
            "TopicID": "topic_id",
            "ActivityType": "kind",
            "Title": "title",
            "Description": "description",
            "Status": "status",
            "SortOrder": "sort_order",
            "TimeLimitMinutes": "time_limit_minutes",
            "MaxAttempts": "max_attempts",
            "GameTemplate": "game_template",
            "IsClosed": "is_closed",
        },
    ),
    (
        "QuizQuestion",
        "quizzes.Question",
        {
            "QuestionID": "id",
            "ActivityID": "activity_id",
            "QuestionText": "text",
            "Marks": "marks",
            "SortOrder": "sort_order",
        },
    ),
    (
        "QuizOption",
        "quizzes.Option",
        {
            "OptionID": "id",
            "QuestionID": "question_id",
            "OptionText": "text",
            "IsCorrect": "is_correct",
        },
    ),
    (
        "SAStatement",
        "assessments.Statement",
        {
            "StatementID": "id",
            "ActivityID": "activity_id",
            "StatementText": "text",
            "SortOrder": "sort_order",
        },
    ),
    (
        "GameGroup",
        "games.Group",
        {"GroupID": "id", "ActivityID": "activity_id", "GroupName": "name"},
    ),
    (
        "GameItem",
        "games.Item",
        {
            "ItemID": "id",
            "ActivityID": "activity_id",
            "GroupID": "group_id",
            "ItemText": "text",
            "MatchText": "match_text",
        },
    ),
    (
        "SimStep",
        "scenarios.Step",
        {
            "StepID": "id",
            "ActivityID": "activity_id",
            "StepText": "text",
            "ImagePath": "image",
            "ImageAlt": "image_alt",
            "IsEnding": "is_ending",
            "Outcome": "outcome",
            "Feedback": "feedback",
        },
    ),
    (
        "SimChoice",
        "scenarios.Choice",
        {
            "ChoiceID": "id",
            "FromStepID": "from_step_id",
            "NextStepID": "next_step_id",
            "ChoiceText": "text",
        },
    ),
    (
        "Payment",
        "payments.Payment",
        {
            "LearnerID": "learner_id",
            "CourseID": "course_id",
            "TransactionUUID": "transaction_uuid",
            "ProviderReference": "provider_reference",
            "AmountNPR": "amount_npr",
            "Status": "status",
            "CreatedDate": "created_at",
            "VerifiedDate": "verified_at",
        },
    ),
    (
        "Enrolment",
        "learning.Enrollment",
        {"LearnerID": "learner_id", "CourseID": "course_id", "EnrolDate": "created_at"},
    ),
    (
        "MaterialCompletion",
        "learning.Completion",
        {"LearnerID": "learner_id", "MaterialID": "material_id", "CompletedDate": "created_at"},
    ),
    (
        "Attempt",
        "activities.Attempt",
        {
            "AttemptID": "id",
            "ActivityID": "activity_id",
            "LearnerID": "learner_id",
            "EndingStepID": "ending_step_id",
            "SubmittedAt": "submitted_at",
            "ScorePercent": "score_percent",
            "TimeTakenSeconds": "time_taken_seconds",
        },
    ),
    (
        "QuizAnswer",
        "quizzes.Answer",
        {
            "AttemptID": "attempt_id",
            "QuestionID": "question_id",
            "SelectedOptionID": "selected_option_id",
        },
    ),
    (
        "SAResponse",
        "assessments.Response",
        {"AttemptID": "attempt_id", "StatementID": "statement_id", "Rating": "rating"},
    ),
    (
        "DiscussionPost",
        "discussions.Post",
        {
            "PostID": "id",
            "ActivityID": "activity_id",
            "UserID": "user_id",
            "ParentPostID": "parent_id",
            "Content": "content",
            "PostedDate": "created_at",
        },
    ),
    (
        "Bookmark",
        "learning.Bookmark",
        {"LearnerID": "learner_id", "MaterialID": "material_id", "CreatedDate": "created_at"},
    ),
    (
        "FAQ",
        "support.FAQ",
        {
            "FAQID": "id",
            "Question": "question",
            "Answer": "answer",
            "Audience": "audience",
            "SortOrder": "sort_order",
        },
    ),
    (
        "ContactMessage",
        "support.ContactMessage",
        {
            "MessageID": "id",
            "UserID": "user_id",
            "SenderName": "sender_name",
            "SenderEmail": "sender_email",
            "Subject": "subject",
            "Message": "message",
            "SentDate": "created_at",
            "IsRead": "is_read",
        },
    ),
]


class Command(BaseCommand):
    help = "Import original demo content/history into an empty database; never overwrite existing users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", type=Path, default=settings.BASE_DIR.parent / "data/legacy_seed.json"
        )
        parser.add_argument("--media-source", type=Path)
        parser.add_argument("--password", default="Password123")

    def handle(self, *args, **options):
        if User.objects.exists():
            raise CommandError(
                "Database already contains users. Import is intentionally non-destructive."
            )
        dataset = json.loads(options["source"].read_text())
        imported_models = []
        with transaction.atomic():
            for table_name, model_label, mapping in TABLES:
                model = apps.get_model(model_label)
                imported_models.append(model)
                for row in dataset.get(table_name, []):
                    values = self.convert_row(model, row, mapping)
                    if model is User:
                        values["password"] = make_password(options["password"])
                    record = model.objects.create(**values)
                    # auto_now fields are correct for application writes, but imported
                    # history must retain its original timestamps.
                    timestamps = {
                        key: value
                        for key, value in values.items()
                        if key in ("created_at", "updated_at", "submitted_at")
                    }
                    if timestamps:
                        model.objects.filter(pk=record.pk).update(**timestamps)
                self.stdout.write(f"{table_name}: {len(dataset.get(table_name, []))}")
            for row in dataset["Activity"]:
                if row.get("StartStepID"):
                    Activity.objects.filter(pk=row["ActivityID"]).update(
                        start_step_id=row["StartStepID"]
                    )
            # Django generates PostgreSQL-specific sequence reset statements after
            # fixed-ID imports, so the next ordinary create gets a fresh ID.
            with connection.cursor() as cursor:
                for statement in connection.ops.sequence_reset_sql(no_style(), imported_models):
                    cursor.execute(statement)
        if options["media_source"]:
            source = options["media_source"] / "Uploads"
            shutil.copytree(source, settings.MEDIA_ROOT / "legacy", dirs_exist_ok=True)
        self.stdout.write(self.style.SUCCESS("Demo imported. Original files were not modified."))

    def convert_row(self, model, row, mapping):
        values = {}
        for legacy_name, field_name in mapping.items():
            if legacy_name not in row:
                continue
            value = row[legacy_name]
            field = model._meta.get_field(
                field_name.removesuffix("_id") if field_name.endswith("_id") else field_name
            )
            if value is None and not field.null:
                if field.get_internal_type() in ("CharField", "TextField", "FileField"):
                    value = ""
                elif field.get_internal_type() == "BooleanField":
                    value = False
                else:
                    value = 0
            if isinstance(value, str) and value.startswith("~/Uploads/"):
                value = "legacy/" + value.removeprefix("~/Uploads/")
            values[field_name] = value
        return values
