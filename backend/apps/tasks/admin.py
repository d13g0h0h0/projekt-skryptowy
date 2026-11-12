from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import SubTask, Task


class SubTaskInline(TabularInline):
    model = SubTask
    extra = 0
    ordering = ("position",)


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("title", "content", "author__username")
    autocomplete_fields = ("author",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [SubTaskInline]