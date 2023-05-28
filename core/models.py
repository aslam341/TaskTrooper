from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", editable=False)
    name = models.CharField(max_length=100)

    def delete_project(self):
        self.delete()

    def __str__(self):
        return f"{self.name}"
    
class Task(models.Model):
    STATUS_CHOICES = (
        ('Not yet started', 'Not yet started'),
        ('In-process', 'In-process'),
        ('Completed', 'Completed'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=100)
    description = models.TextField()

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def delete_task(self):
        self.delete()

    def __str__(self):
        return f"{self.name}"
