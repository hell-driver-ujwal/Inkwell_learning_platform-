"""Account workflows: lockout, role portals and administrator changes."""

from datetime import timedelta

from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import AccountStatus, User, UserRole


def authenticate_portal(*, email, password, role):
    """Check credentials while committing failed-login counters even on failure."""
    error = None
    authenticated_user = None
    with transaction.atomic():
        user = User.objects.select_for_update().filter(email__iexact=email).first()
        if user is None:
            # Django's hasher also runs for unknown users to reduce timing disclosure.
            User().set_password(password)
            error = "Email or password is incorrect."
        elif user.locked_until and user.locked_until > timezone.now():
            error = "Account temporarily locked. Try again in 15 minutes."
        elif not user.check_password(password):
            if user.locked_until and user.locked_until <= timezone.now():
                user.failed_login_count = 0
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                user.locked_until = timezone.now() + timedelta(minutes=15)
            user.save(update_fields=["failed_login_count", "locked_until"])
            error = "Email or password is incorrect."
        elif user.role != role:
            error = "Use the sign-in page for your account's role."
        elif user.status != AccountStatus.ACTIVE or not user.is_active:
            error = "This account is pending approval, rejected or deactivated."
        else:
            user.failed_login_count = 0
            user.locked_until = None
            user.save(update_fields=["failed_login_count", "locked_until"])
            authenticated_user = user
    if error:
        raise ValidationError(error)
    return authenticated_user


def change_password(*, request, password):
    """Keep the current session valid after replacing a temporary password."""
    user = request.user
    user.set_password(password)
    user.must_change_password = False
    user.save(update_fields=["password", "must_change_password"])
    update_session_auth_hash(request, user)


@transaction.atomic
def administer_account(*, administrator, user_id, action, password=None):
    """Prevent platform administrators from changing administrator peers."""
    from accounts.permissions import require_administrator

    require_administrator(administrator)
    user = User.objects.select_for_update().get(pk=user_id)
    if user.role == UserRole.ADMIN:
        raise PermissionDenied("Administrator accounts cannot be managed here.")
    if action == "unlock":
        user.failed_login_count = 0
        user.locked_until = None
    elif action in ("approve", "reject"):
        if user.role != UserRole.TEACHER or user.status != AccountStatus.PENDING:
            raise ValidationError("Only pending lecturer applications can be reviewed.")
        user.status = AccountStatus.ACTIVE if action == "approve" else AccountStatus.REJECTED
    elif action == "deactivate":
        user.status = AccountStatus.DEACTIVATED
    elif action == "activate":
        user.status = AccountStatus.ACTIVE
    elif action == "reset_password":
        user.set_password(password)
        user.must_change_password = True
    user.save()
    return user


@transaction.atomic
def delete_account(*, administrator, user):
    """Mirror original deletion rules; payment history and authored courses block removal."""
    from activities.models import Attempt
    from discussions.models import Post
    from payments.models import Payment

    from accounts.permissions import require_administrator

    require_administrator(administrator)
    user = User.objects.select_for_update().get(pk=user.pk)
    if user.role == UserRole.ADMIN:
        raise PermissionDenied("Administrator accounts cannot be deleted.")
    if user.authored_courses.exists() or Payment.objects.filter(learner=user).exists():
        raise ValidationError(
            "This account owns courses or payment history. Deactivate it instead."
        )
    Attempt.objects.filter(learner=user).delete()
    Post.objects.filter(user=user).delete()
    user.delete()
