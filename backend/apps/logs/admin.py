from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ErrorLog


@admin.register(ErrorLog)
class ErrorLogAdmin(ModelAdmin):
    list_display = ("created_at", "level", "status_code", "method", "path", "username", "short_message")
    list_filter = ("level", "status_code", "created_at")
    search_fields = ("message", "path", "traceback", "username")
    date_hierarchy = "created_at"

    @admin.display(description="Message")
    def short_message(self, obj):
        return obj.message[:80]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False