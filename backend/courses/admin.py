"""Read-only inspection of courses records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from courses.models import Course, Material, Subject, Topic

admin.site.register(Subject, InspectionAdmin)
admin.site.register(Course, InspectionAdmin)
admin.site.register(Topic, InspectionAdmin)
admin.site.register(Material, InspectionAdmin)
