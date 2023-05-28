from django import forms
from .models import Project, Task


class AddProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

