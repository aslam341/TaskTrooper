from django.db import models
from django.contrib.auth.models import User
import uuid
from phonenumber_field.modelfields import PhoneNumberField
import os

class Project(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_projects", editable=False, null=True)

    invite_code = models.CharField(max_length=7, blank=True, null=True)
    users = models.ManyToManyField(User, through='ProjectPermission', related_name="joined_projects")

    def delete_project(self):
        self.delete()

    def addUser(self, user):
        if not self.users.filter(id=user.id).exists():
            self.users.add(user)
            project_permission, created = ProjectPermission.objects.get_or_create(
                project=self,
                user=user,
                defaults={'permission': 'read'}  # Grant 'read' permission if it's a new ProjectPermission
            )
            # For some reason, code does not work if the below code is not included, although the below code is never executed
            if not created:
                project_permission.permission = 'read'
                project_permission.save()
                
            # Create a user profile for the user in this project
            UserProfile.objects.create(user=user, project=self)

    def removeUser(self, user):
        self.users.remove(user)
        ProjectPermission.objects.filter(project=self, user=user).delete()
        # Delete the associated UserProfile for the user in this project
        UserProfile.objects.filter(user=user, project=self).delete()

    def updatePermission(self, user, new_permission):
        project_permission = ProjectPermission.objects.filter(project=self, user=user).first()
        if project_permission:
            project_permission.permission = new_permission
            project_permission.save()
    
    def save(self, *args, **kwargs):
        is_new_project = self.pk is None  # Check if it's a new project being created
        if is_new_project:
            if not self.invite_code:
                self.invite_code = str(uuid.uuid4())[:7]
            super().save(*args, **kwargs)  # Save the project instance first

            # Create ProjectPermission for the creator with 'creator' permission
            ProjectPermission.objects.create(
                project=self,
                user=self.creator,
                permission='creator'
            )
            UserProfile.objects.create(user=self.creator, project=self)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
class ProjectPermission(models.Model):
    PERMISSION_CHOICES = (
        ('read', 'Read'),
        ('add_users', 'Add Users'),
        ('create_tasks', 'Create Tasks'),
        ('modify_tasks', 'Modify Tasks'),
        ('delete_tasks', 'Delete Tasks'),
        ('modify_other_users_permissions', 'Modify Other Users Permissions'),
        ('delete_users', 'Delete Users'),
        ('delete_project', 'Delete Project'),
        ('creator', 'Creator')
    )

    PERMISSION_LEVELS = {
        'read': 1,
        'add_users': 2,
        'create_tasks': 3,
        'modify_tasks': 4,
        'delete_tasks': 5,
        'modify_other_users_permissions': 6,
        'delete_users': 7,
        'delete_project': 8,
        'creator': 9
    }

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="permissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_permissions")
    permission = models.CharField(max_length=30, choices=PERMISSION_CHOICES)

    nickname = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('project', 'user')

    def has_permission(self, target_permission):
        return self.PERMISSION_LEVELS[self.permission] >= self.PERMISSION_LEVELS[target_permission]
    
    def permission_level(self):
        return self.PERMISSION_LEVELS.get(self.permission, 0)

    
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="user_profiles")
    display_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    phone_number = PhoneNumberField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username} in {self.project.name}"
    
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
    users = models.ManyToManyField(User, related_name='tasks')

    def delete_task(self):
        self.delete()

    def __str__(self):
        return f"{self.name}"
    
class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_files', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_files', null=True, blank=True)
    file = models.FileField(upload_to='files/')

    def __str__(self):
        return self.file.name
    
    def delete(self, *args, **kwargs):
        # Get the file path before deleting the model instance
        file_path = self.file.path
        super().delete(*args, **kwargs)
        # Delete the associated file from the storage
        if os.path.exists(file_path):
            os.remove(file_path)

