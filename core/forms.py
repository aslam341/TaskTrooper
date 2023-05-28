from django import forms
from .models import Project, Task


class AddProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class AddTaskForm(forms.ModelForm):
    def __init__(self, project_id, *args, **kwargs):
        super(AddTaskForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(id=project_id) # For security reason, this line prevents users from seeing other users' projects
        self.fields['project'].initial = project_id
        self.fields['project'].disabled = True

    class Meta:
        model = Task
        fields = '__all__'

class ChangeTaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }