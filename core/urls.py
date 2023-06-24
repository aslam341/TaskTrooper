from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('myprojects/', views.myprojects, name='myprojects'), # Overview of all projects
    path('myprojects/addproject', views.addproject, name='addproject'), # Add a project
    path('myprojects/<int:project_id>/', views.project, name='project'), # Overview of a project
    path('myprojects/<int:project_id>/deleteproject', views.deleteproject, name='deleteproject'), # Delete a project
    path('myprojects/<int:project_id>/usermanagement/', views.user_management, name='user_management'), # Bulk modify users' permissions
    path('myprojects/<int:project_id>/projectmanagement/', views.project_management, name='project_management'), # Manage a project
    path('myprojects/<int:project_id>/updateprojectname/', views.update_project_name, name='updateprojectname'),
    path('myprojects/<str:invite_link>/join', views.joinproject, name='joinproject'), # Join a project
    path('myprojects/<int:project_id>/addtask', views.addtask, name='addtask'), # Add a task
    path('myprojects/<int:project_id>/<int:task_id>/', views.taskproperties, name='taskproperties'), # Overview of a task
    path('myprojects/<int:project_id>/<int:task_id>/deletetask', views.deletetask, name='deletetask'), # Delete a task
    path('myprojects/<int:project_id>/<int:task_id>/changetaskstatus', views.changetaskstatus, name='changetaskstatus') # Change a task's status
]