from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Project, Task, ProjectPermission, UserProfile, File
import os


# Unit Tests for Models

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)

    def test_delete_project(self):
        self.project.delete_project()
        self.assertFalse(Project.objects.filter(name='Test Project').exists())

    def test_add_user(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.project.addUser(new_user)
        self.assertTrue(self.project.users.filter(id=new_user.id).exists())

    def test_remove_user(self):
        self.project.removeUser(self.user)
        self.assertFalse(self.project.users.filter(id=self.user.id).exists())

    def test_update_permission(self):
        permission = 'add_users'
        self.project.updatePermission(self.user, permission)
        project_permission = ProjectPermission.objects.filter(project=self.project, user=self.user).first()
        self.assertEqual(project_permission.permission, permission)

    def test_save_new_project(self):
        project = Project(name='New Project', creator=self.user)
        project.save()
        self.assertIsNotNone(project.invite_code)
        self.assertTrue(ProjectPermission.objects.filter(project=project, user=self.user, permission='creator').exists())

    def test_save_existing_project(self):
        project = Project.objects.create(name='Existing Project', creator=self.user)
        project.name = 'Updated Project'
        project.save()
        self.assertEqual(Project.objects.get(id=project.id).name, 'Updated Project')

class ProjectPermissionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)

    def test_has_permission(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.project.addUser(new_user)
        self.project.updatePermission(new_user, 'add_users')
        project_permission = ProjectPermission.objects.get(project=self.project, user=new_user)
        self.assertTrue(project_permission.has_permission('add_users'))
        self.assertTrue(project_permission.has_permission('read'))
        self.assertFalse(project_permission.has_permission('modify_tasks'))

    def test_permission_level(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.project.addUser(new_user)
        self.project.updatePermission(new_user, 'add_users')
        project_permission = ProjectPermission.objects.get(project=self.project, user=new_user)
        self.assertEqual(project_permission.permission_level(), 2)

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            description='This is a test task',
            start_datetime='2023-07-23 10:00:00',
            end_datetime='2023-07-23 12:00:00',
            status='Not yet started'
        )

    def test_delete_task(self):
        self.task.delete_task()
        self.assertFalse(Task.objects.filter(name='Test Task').exists())

    def test_task_users(self):
        user1 = User.objects.create_user(username='user1', password='password1')
        user2 = User.objects.create_user(username='user2', password='password2')
        self.task.users.add(user1, user2)
        self.assertEqual(self.task.users.count(), 2)
        self.assertIn(user1, self.task.users.all())
        self.assertIn(user2, self.task.users.all())

class FileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            description='This is a test task',
            start_datetime='2023-07-23 10:00:00',
            end_datetime='2023-07-23 12:00:00',
            status='Not yet started'
        )

    def test_file_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        file_content = b'Test file content'
        file = SimpleUploadedFile("test_file.txt", file_content)
        file_obj = File.objects.create(project=self.project, file=file)
        self.assertEqual(file_obj.file.read(), file_content)

    def test_file_delete_on_instance_delete(self):
        from django.core.files.base import ContentFile
        file_content = b'Test file content'
        file = ContentFile(file_content, name="test_file.txt")
        file_obj = File.objects.create(project=self.project, file=file)
        file_path = file_obj.file.path
        self.assertTrue(os.path.exists(file_path))
        file_obj.delete()
        self.assertFalse(os.path.exists(file_path))

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)

    def test_profile_creation_on_project_user_add(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.project.addUser(new_user)
        profile = UserProfile.objects.get(user=new_user, project=self.project)
        self.assertIsNone(profile.display_name)
        self.assertIsNone(profile.role)
        self.assertIsNone(profile.phone_number)
        self.assertIsNone(profile.email_address)

    def test_profile_deletion_on_project_user_remove(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.project.addUser(new_user)
        self.project.removeUser(new_user)
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(user=new_user, project=self.project)

    def test_profile_str_representation(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword')
        self.project.addUser(new_user)
        profile = UserProfile.objects.get(user=new_user, project=self.project)
        self.assertEqual(str(profile), f"Profile for {new_user.username} in {self.project.name}")

class ProjectManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_project_manager(self):
        projects = Project.objects.all()
        self.assertEqual(len(projects), 0)

        project1 = Project.objects.create(name='Project 1', creator=self.user)
        projects = Project.objects.all()  # Reassign the queryset to reflect the latest changes
        self.assertEqual(len(projects), 1)

        project2 = Project.objects.create(name='Project 2', creator=self.user)
        projects = Project.objects.all()  # Reassign the queryset again
        self.assertEqual(len(projects), 2)