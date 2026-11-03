from django.db import models
from django.conf import settings


class Task(models.Model):
    content = models.TextField(verbose_name="Task content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tasks")
    title = models.CharField()


    def __str__(self):
        return self.title


class SubTask(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="subtasks"
    )
    content = models.CharField(max_length=255, verbose_name="Subtask content")
    position = models.PositiveSmallIntegerField()
