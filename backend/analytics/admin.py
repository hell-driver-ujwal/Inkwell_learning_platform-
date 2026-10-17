"""Read-only inspection of analytics records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from analytics.models import PageView

admin.site.register(PageView, InspectionAdmin)
