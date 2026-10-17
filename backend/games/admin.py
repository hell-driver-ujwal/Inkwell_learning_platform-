"""Read-only inspection of games records in Django admin."""

from common.admin import InspectionAdmin
from django.contrib import admin

from games.models import Group, Item

admin.site.register(Group, InspectionAdmin)
admin.site.register(Item, InspectionAdmin)
