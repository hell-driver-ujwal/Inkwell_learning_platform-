"""Read-only inspection of accounts records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from accounts.models import User

admin.site.register(User, InspectionAdmin)
