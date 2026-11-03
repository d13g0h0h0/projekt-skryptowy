from django.db import models
from django.conf import settings

class Solution(models.Model): #add images in v2
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="solutions")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="solutions")
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SolutionPart(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE,related_name="parts")
    subtask = models.ForeignKey("tasks.Subtask", on_delete=models.PROTECT,related_name="solution_parts")
    content = models.TextField()

class Vote(models.Model):
    class Value(models.IntegerChoices):
        UP=1
        DOWN=-1

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes")
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name="votes")
    value = models.SmallIntegerField(choices=Value.choices)
    created_at = models.DateTimeField(auto_now_add=True)

class GivenUpTask (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="give_ups")
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="give_ups")
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback (models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name="feedback")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="given_feedback")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

