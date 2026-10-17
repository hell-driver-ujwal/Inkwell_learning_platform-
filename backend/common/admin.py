"""Read-only maintenance inspection cannot bypass domain services."""

from django.contrib import admin


class InspectionAdmin(admin.ModelAdmin):
    """Use the React author/admin workflows for changes that need business rules."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
