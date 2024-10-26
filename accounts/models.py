from django.db import models
from django.contrib.auth.models import User
from course_manager.models import Course, LabBook
# Create your models here.


ROLES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True)
    role = models.CharField(max_length=20,choices=ROLES, default='student')

    def __str__(self):
        return self.user.username
