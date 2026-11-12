from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import TeacherProfile, TeacherStudentLink


@admin.register(TeacherStudentLink)
class TeacherStudentLinkAdmin(ModelAdmin):
    list_display = ("id", "student", "teacher", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__username", "teacher__username")
    autocomplete_fields = ("student", "teacher")
    readonly_fields = ("created_at",)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(ModelAdmin):
    list_display = ("user", "specialization")
    search_fields = ("user__username", "bio")
    autocomplete_fields = ("user",)