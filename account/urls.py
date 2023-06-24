from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'account'

urlpatterns = [
    path('', lambda request: redirect('login'), name='login'),
    path("signup/", views.signup, name="signup"),
]