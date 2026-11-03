from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TeacherStudentLink(models.Model):
    class Status(models.TextChoices):
        PENDING= "pending"
        ACTIVE="active"
        DECLINED="declined"
        CANCELLED="cancelled"

    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="teacher_links")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_links")
    status = models.CharField(choices=Status.choices,default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True,blank=True)
    cancelled_at =  models.DateTimeField(null=True,blank=True)

    class Meta:
        constraints= [
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(status__in=["pending","active"]),
                name="one_open_link_per_student"
            )
        ]

def validate_specialization(value: list[str]) -> None:
    invalid = set(value) - set(TeacherProfile.Specialization.values)
    if invalid:
        raise ValidationError(f"Invalid set of specializations: {invalid}")

class TeacherProfile(models.Model):
    class Specialization(models.TextChoices):
        ALGEBRA = "algebra",
        COMBINATORICS = "combinatorics"
        GEOMETRY = "geometry"
        NUMBER_THEORY = "number_theory"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,primary_key=True, related_name="teacher_profile")
    bio = models.TextField(blank=True)
    specialization = models.JSONField(default=list,blank=True, validators=[validate_specialization])