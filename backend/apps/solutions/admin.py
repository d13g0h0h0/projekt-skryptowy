from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Feedback, GivenUpTask, Solution, SolutionPart, Vote


class SolutionPartInline(TabularInline):
    model = SolutionPart
    extra = 0


class FeedbackInline(TabularInline):
    model = Feedback
    extra = 0
    autocomplete_fields = ("teacher",)


@admin.register(Solution)
class SolutionAdmin(ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "task__title", "author__username")
    autocomplete_fields = ("task", "author")
    readonly_fields = ("created_at", "updated_at")
    inlines = [SolutionPartInline, FeedbackInline]


@admin.register(Vote)
class VoteAdmin(ModelAdmin):
    list_display = ("id", "solution", "user", "value", "created_at")
    list_filter = ("value",)
    autocomplete_fields = ("solution", "user")


@admin.register(GivenUpTask)
class GivenUpTaskAdmin(ModelAdmin):
    list_display = ("id", "task", "user", "created_at")
    autocomplete_fields = ("task", "user")


@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    list_display = ("id", "solution", "teacher", "created_at")
    search_fields = ("content", "teacher__username")
    autocomplete_fields = ("solution", "teacher")