from django.db import models
from django.contrib.auth.models import User


# Create your models here.

ROLES = (
    ('student', 'Student'),
    ('teacher', 'Teacher'),
)

class Course(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

class LabBook(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    owner_role = models.CharField(max_length=20, choices=ROLES, default='student')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')

