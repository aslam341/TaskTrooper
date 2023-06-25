from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, Task, ProjectPermission
from .forms import AddProjectForm, AddTaskForm

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