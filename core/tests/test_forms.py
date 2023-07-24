from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from ..models import Project, Task, ProjectPermission, UserProfile, File
from ..forms import AddProjectForm, AddTaskForm, BulkModifyPermissionForm, BulkRemoveUserForm, ChangeTaskStatusForm, ModifyTaskForm, UserProfileForm
import os


# Unit Tests for Forms

class AddProjectFormTest(TestCase):
    def test_form_valid(self):
        form_data = {'name': 'Test Project'}
        form = AddProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {'name': ''}
        form = AddProjectForm(data=form_data)
        self.assertFalse(form.is_valid())


class AddTaskFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)

    def test_form_valid(self):
        form_data = {
            'project': self.project.id,
            'name': 'Test Task',
            'description': 'Test Description',
            'start_datetime': '2023-06-26 10:00',
            'end_datetime': '2023-06-26 12:00',
            'status': 'Not yet started',
            'users': [self.user.id],
        }
        form = AddTaskForm(project_id=self.project.id, data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid1(self):
        form_data = {
            'project': self.project.id,
            'name': '',
            'description': 'Test Description',
            'start_datetime': '2023-06-26 10:00',
            'end_datetime': '2023-06-26 12:00',
            'status': 'Not yet started',
            'users': [self.user.id],
        }
        form = AddTaskForm(project_id=self.project.id, data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_invalid2(self):
        form_data = {
            'project': self.project.id,
            'name': 'Test Task',
            'description': 'Test Description',
            'start_datetime': '2023-06-26 12:00',
            'end_datetime': '2023-06-26 10:00',
            'status': 'Not yet started',
            'users': [self.user.id],
        }
        form = AddTaskForm(project_id=self.project.id, data=form_data)
        self.assertFalse(form.is_valid())

class BulkModifyPermissionFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')
        self.project = Project.objects.create(name='Test Project', creator=self.user1)
        self.project.addUser(self.user2)
        self.project.addUser(self.user3)
        self.project.updatePermission(self.user2, 'delete_tasks')

    def test_form_valid(self):
        form_data = {
            'selected_users': [self.user2.id],
            'new_permission': 'add_users',
        }
        request = RequestFactory().get('/')
        request.user = self.user1
        form = BulkModifyPermissionForm(project=self.project, request=request, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'selected_users': [self.user2.id],
            'new_permission': 'delete_project',
        }
        request = RequestFactory().get('/')
        request.user = self.user2
        form = BulkModifyPermissionForm(project=self.project, request=request, data=form_data)
        self.assertFalse(form.is_valid())

class BulkRemoveUserFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')
        self.project = Project.objects.create(name='Test Project', creator=self.user1)
        self.project.addUser(self.user2)
        self.project.addUser(self.user3)
        self.project.updatePermission(self.user2, 'delete_tasks')
        self.project.updatePermission(self.user3, 'delete_project')

    def test_form_valid(self):
        form_data = {
            'selected_users': [self.user2.id],
        }
        request = RequestFactory().get('/')
        request.user = self.user1
        form = BulkRemoveUserForm(project=self.project, request=request, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'selected_users': [self.user3.id],
        }
        request = RequestFactory().get('/')
        request.user = self.user2
        form = BulkRemoveUserForm(project=self.project, request=request, data=form_data)
        self.assertFalse(form.is_valid())

class ChangeTaskStatusFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            description='Test Description',
            start_datetime='2023-06-26 10:00',
            end_datetime='2023-06-26 12:00',
            status='Not yet started',
        )

    def test_form_valid(self):
        form_data = {
            'status': 'In-process',
        }
        form = ChangeTaskStatusForm(instance=self.task, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'status': '',
        }
        form = ChangeTaskStatusForm(instance=self.task, data=form_data)
        self.assertFalse(form.is_valid())

class ModifyTaskFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)
        self.task = Task.objects.create(
            project=self.project,
            name='Test Task',
            description='Test Description',
            start_datetime='2023-06-26 10:00',
            end_datetime='2023-06-26 12:00',
            status='Not yet started',
        )

    def test_form_valid(self):
        form_data = {
            'name': 'Modified Task',
            'description': 'Modified Description',
            'start_datetime': '2023-06-26 11:00',
            'end_datetime': '2023-06-26 13:00',
            'status': 'In-process',
            'users': [self.user.id],
            'new_files': None,
        }
        form = ModifyTaskForm(project=self.project, instance=self.task, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'name': '',
            'description': 'Modified Description',
            'start_datetime': '2023-06-26 11:00',
            'end_datetime': '2023-06-26 13:00',
            'status': 'In-process',
            'users': [self.user.id],
            'new_files': None,
        }
        form = ModifyTaskForm(project=self.project, instance=self.task, data=form_data)
        self.assertFalse(form.is_valid())

class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.project = Project.objects.create(name='Test Project', creator=self.user)
        self.user_profile = UserProfile.objects.create(user=self.user, project=self.project)

    def test_form_valid1(self):
        form_data = {
            'display_name': 'John Doe',
            'role': 'Developer',
            'phone_number': '+65 9876 5432',
            'email_address': 'example@gmail.com',
        }
        form = UserProfileForm(instance=self.user_profile, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valid2(self):
        form_data = {
            'display_name': 'John Doe',
            'role': '',
            'phone_number': '+65 9876 5432',
            'email_address': 'example@gmail.com',
        }
        form = UserProfileForm(instance=self.user_profile, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_phonenumber(self):
        form_data = {
            'display_name': 'John Doe',
            'role': '',
            'phone_number': '9876 5432',
            'email_address': 'example@gmail.com',
        }
        form = UserProfileForm(instance=self.user_profile, data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_phonenumber(self):
        form_data = {
            'display_name': 'John Doe',
            'role': '',
            'phone_number': '+65 9876 5432',
            'email_address': 'examplegmail.com',
        }
        form = UserProfileForm(instance=self.user_profile, data=form_data)
        self.assertFalse(form.is_valid())