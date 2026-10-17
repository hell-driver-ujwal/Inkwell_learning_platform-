"""Read-only inspection of learning records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from learning.models import Bookmark, Completion, Enrollment, Review

admin.site.register(Enrollment, InspectionAdmin)
admin.site.register(Completion, InspectionAdmin)
admin.site.register(Bookmark, InspectionAdmin)
admin.site.register(Review, InspectionAdmin)
