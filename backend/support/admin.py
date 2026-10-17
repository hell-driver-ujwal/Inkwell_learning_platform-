"""Read-only inspection of support records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from support.models import FAQ, ContactMessage

admin.site.register(FAQ, InspectionAdmin)
admin.site.register(ContactMessage, InspectionAdmin)
