"""Read-only inspection of payments records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from payments.models import Payment

admin.site.register(Payment, InspectionAdmin)
