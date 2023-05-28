from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('myprojects/', views.myprojects, name='myprojects'),
    path('myprojects/addproject', views.addproject, name='addproject'),
    path('myprojects/<int:project_id>/', views.project, name='project'),
    path('myprojects/<int:project_id>/addtask', views.addtask, name='addtask')
]