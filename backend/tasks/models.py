from django.db import models

class Task(models.Model):
    content = models.TextField(verbose_name="Task content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task #{self.id}"


class SubTask(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="subtasks",
        verbose_name="Parent task"
    )
    content = models.CharField(max_length=255, verbose_name="Subtask content")

    def __str__(self):
        return self.content