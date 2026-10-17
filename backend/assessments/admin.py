"""Read-only inspection of assessments records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from assessments.models import Response, Statement

admin.site.register(Statement, InspectionAdmin)
admin.site.register(Response, InspectionAdmin)
