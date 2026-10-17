"""Read-only inspection of activities records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from activities.models import Activity, Attempt, PlaySession

admin.site.register(Activity, InspectionAdmin)
admin.site.register(Attempt, InspectionAdmin)
admin.site.register(PlaySession, InspectionAdmin)
