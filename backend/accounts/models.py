"""Email-based users with explicit platform roles and approval status."""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower


class UserRole(models.TextChoices):
    LEARNER = "Learner", "Learner"
    TEACHER = "Teacher", "Lecturer"
    ADMIN = "Admin", "Administrator"


class AccountStatus(models.TextChoices):
    ACTIVE = "Active", "Active"
    PENDING = "Pending", "Pending"
    REJECTED = "Rejected", "Rejected"
    DEACTIVATED = "Deactivated", "Deactivated"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create a user using Django's password hashing."""
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create a trusted maintenance account for Django admin."""
        extra_fields.update(is_staff=True, is_superuser=True, role=UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=7, choices=UserRole.choices, default=UserRole.LEARNER)
    status = models.CharField(
        max_length=11, choices=AccountStatus.choices, default=AccountStatus.ACTIVE
    )
    application_reason = models.CharField(max_length=500, blank=True)
    failed_login_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=UserRole.values), name="user_valid_role"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=AccountStatus.values), name="user_valid_status"
            ),
            models.UniqueConstraint(Lower("email"), name="user_email_case_insensitive"),
        ]

    def __str__(self):
        return self.full_name or self.email
