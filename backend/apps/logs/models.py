from django.db import models


class ErrorLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=20)
    logger = models.CharField(max_length=100)
    message = models.TextField()
    traceback = models.TextField(blank=True)
    method = models.CharField(max_length=10, blank=True)
    path = models.CharField(max_length=500, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    username = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.level} {self.path or self.logger}"