"""Read-only inspection of scenarios records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from scenarios.models import Choice, Step

admin.site.register(Step, InspectionAdmin)
admin.site.register(Choice, InspectionAdmin)
