from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Project, Task, ProjectPermission, UserProfile, File


# Unit Tests for Views

class ViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_home_view(self):
        client = Client()
        response = client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 302)

        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_addproject_view(self):
        client = Client()
        response = client.get(reverse('core:addproject'))
        self.assertEqual(response.status_code, 302)

        client.login(username='testuser', password='testpassword')
        response = client.get(reverse('core:addproject'))
        self.assertEqual(response.status_code, 200)

        response = client.post(reverse('core:addproject'), {'name': 'Test Project'})
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Project.objects.filter(name='Test Project').exists())

        self.assertEqual(self.user.created_projects.count(), 1)

    def test_deleteproject_view(self):
        client = Client()

        client.login(username='testuser', password='testpassword')

        project = Project.objects.create(name='Test Project', creator=self.user)

        self.assertTrue(Project.objects.filter(name='Test Project').exists())

        response = client.post(reverse('core:deleteproject', args=[project.id]))
        self.assertEqual(response.status_code, 302)

        self.assertFalse(Project.objects.filter(name='Test Project').exists())

    def test_project_view(self):
        client = Client()

        client.login(username='testuser', password='testpassword')

        project = Project.objects.create(name='Test Project', creator=self.user)

        self.assertTrue(Project.objects.filter(name='Test Project').exists())

        response = client.get(reverse('core:project', args=[project.id]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['project'], project)
        self.assertEqual(list(response.context['tasks']), list(project.tasks.all()))

    def test_myprojects_view(self):
        client = Client()

        response = client.get(reverse('core:myprojects'))
        self.assertEqual(response.status_code, 302)

        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:myprojects'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(list(response.context['created_projects']), list(self.user.created_projects.all()))
        self.assertEqual(list(response.context['joined_projects']), list(self.user.joined_projects.exclude(creator=self.user)))

    def test_joinproject_view(self):
        client = Client()
        project = Project.objects.create(name='Test Project', creator=self.user, invite_code='abcdef')

        response = client.get(reverse('core:joinproject', args=[project.invite_code]))
        self.assertEqual(response.status_code, 302) 

        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:joinproject', args=[project.invite_code]))
        self.assertEqual(response.status_code, 302)

        self.assertTrue(project.users.filter(id=self.user.id).exists())

    def test_allusers_view(self):
        client = Client()

        project = Project.objects.create(name='Test Project', creator=self.user)
        user1 = User.objects.create_user(username='user1', password='user1password')
        user2 = User.objects.create_user(username='user2', password='user2password')
        project.addUser(user1)
        project.addUser(user2)

        response = client.get(reverse('core:allusers', args=[project.id]))
        self.assertEqual(response.status_code, 302)

        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:allusers', args=[project.id]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['project'], project)
        self.assertEqual(list(response.context['users']), list(project.users.all()))

    def test_addtask_view(self):
        client = Client()

        project = Project.objects.create(name='Test Project', creator=self.user)
        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:addtask', args=[project.id]))
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'Test Task',
            'description': 'This is a test task',
            'start_datetime': '2023-07-24 10:00',
            'end_datetime': '2023-07-24 12:00',
            'status': 'Not yet started',
            'users': [self.user.id],
        }
        response = client.post(reverse('core:addtask', args=[project.id]), data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(project.tasks.filter(name='Test Task').exists())

    def test_taskproperties_view(self):
        client = Client()

        project = Project.objects.create(name='Test Project', creator=self.user)
        task = Task.objects.create(project=project, name='Test Task', description='This is a test task',
                                   start_datetime='2023-07-24 10:00', end_datetime='2023-07-24 12:00', status='Not yet started')
        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:taskproperties', args=[project.id, task.id]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['project'], project)
        self.assertEqual(response.context['task'], task)

    def test_changetaskstatus_view(self):
        client = Client()

        project = Project.objects.create(name='Test Project', creator=self.user)
        task = Task.objects.create(project=project, name='Test Task', description='This is a test task',
                                   start_datetime='2023-07-24 10:00', end_datetime='2023-07-24 12:00', status='Not yet started')
        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:changetaskstatus', args=[project.id, task.id]))
        self.assertEqual(response.status_code, 200)

        data = {'status': 'In-process'}
        response = client.post(reverse('core:changetaskstatus', args=[project.id, task.id]), data)
        self.assertEqual(response.status_code, 302)

        task.refresh_from_db()
        self.assertEqual(task.status, 'In-process')

    def test_edit_user_profile_view(self):
        client = Client()

        project = Project.objects.create(name='Test Project', creator=self.user)
        user_profile = UserProfile.objects.get(user=self.user, project=project)

        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:edituserprofile', args=[project.id]))
        self.assertEqual(response.status_code, 200)

        data = {
            'display_name': 'Updated User',
            'role': 'Developer',
            'phone_number': '+65 9022 4812',
            'email_address': 'updated@example.com',
        }
        response = client.post(reverse('core:edituserprofile', args=[project.id]), data)
        self.assertEqual(response.status_code, 302)

        user_profile.refresh_from_db()
        self.assertEqual(user_profile.display_name, 'Updated User')
        self.assertEqual(user_profile.role, 'Developer')
        self.assertEqual(user_profile.phone_number, '+6590224812')
        self.assertEqual(user_profile.email_address, 'updated@example.com')

    def test_user_management_view(self):
        client = Client()

        project = Project.objects.create(name='Test Project', creator=self.user)
        user1 = User.objects.create_user(username='user1', password='user1password')
        user2 = User.objects.create_user(username='user2', password='user2password')
        ProjectPermission.objects.create(project=project, user=user1, permission='read')
        ProjectPermission.objects.create(project=project, user=user2, permission='add_users')
        UserProfile.objects.create(user=user1, project=project, display_name='User 1')
        UserProfile.objects.create(user=user2, project=project, display_name='User 2')

        client.login(username='testuser', password='testpassword')

        response = client.get(reverse('core:user_management', args=[project.id]))
        self.assertEqual(response.status_code, 200)

        data = {
            'selected_users': [user1.id, user2.id],
            'new_permission': 'modify_tasks',
        }
        response = client.post(reverse('core:user_management', args=[project.id]), data)
        self.assertEqual(response.status_code, 302)

        user1_permission = ProjectPermission.objects.get(project=project, user=user1)
        user2_permission = ProjectPermission.objects.get(project=project, user=user2)
        self.assertEqual(user1_permission.permission, 'modify_tasks')
        self.assertEqual(user2_permission.permission, 'modify_tasks')

        data = {
            'selected_users': [user1.id, user2.id],
        }
        response = client.post(reverse('core:user_management', args=[project.id]), data)
        self.assertEqual(response.status_code, 302)

        self.assertFalse(project.users.filter(id=user1.id).exists())
        self.assertFalse(project.users.filter(id=user2.id).exists())

    