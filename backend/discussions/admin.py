"""Read-only inspection of discussions records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from discussions.models import Post

admin.site.register(Post, InspectionAdmin)
