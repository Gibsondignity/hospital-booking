from django.contrib import admin

from .models import AuditLog, ClinicConfiguration, StaffProfile


@admin.register(ClinicConfiguration)
class ClinicConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "currency", "is_active")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("staff_id", "user", "role", "employment_status", "is_active")
    list_filter = ("role", "employment_status", "is_active")
    search_fields = ("staff_id", "user__first_name", "user__last_name", "phone")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor", "action", "resource_type", "resource_id")
    list_filter = ("action", "resource_type")
    readonly_fields = ("actor", "action", "resource_type", "resource_id", "metadata", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
