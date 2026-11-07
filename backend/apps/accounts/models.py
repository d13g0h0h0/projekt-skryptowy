from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student","Student"
        TEACHER = "teacher", "Teacher"

    email = models.EmailField(unique=True)
    role = models.CharField(choices=Role.choices,default=Role.STUDENT)

    @property
    def is_teacher(self) -> bool:
        return self.role == self.Role.TEACHER

