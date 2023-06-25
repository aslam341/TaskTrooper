from django import forms
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from .models import Project, Task, ProjectPermission
from django.contrib.auth.models import User
from django.db.models import Q, F


class BulkModifyPermissionForm(forms.Form):
    selected_users = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    new_permission = forms.ChoiceField(choices=ProjectPermission.PERMISSION_CHOICES)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        current_user_permission = ProjectPermission.objects.filter(
            project=project,
            user=request.user
        ).first().permission

        users = project.users.exclude(
            id=request.user.id
        ).exclude(
            id=project.creator.id
        )

        filtered_users = []
        for user in users:
            user_permission = ProjectPermission.PERMISSION_LEVELS.get(
                project.permissions.filter(user=user).first().permission
            )
            if user_permission is not None and user_permission < ProjectPermission.PERMISSION_LEVELS.get(current_user_permission):
                filtered_users.append((user.id, user.username))

        self.fields['selected_users'].choices = filtered_users

        permission_choices = [
            (key, value) for key, value in ProjectPermission.PERMISSION_CHOICES
            if key != 'creator' and ProjectPermission.PERMISSION_LEVELS.get(key) <= ProjectPermission.PERMISSION_LEVELS.get(current_user_permission)
        ]
        self.fields['new_permission'].choices = permission_choices

class BulkRemoveUserForm(forms.Form):
    selected_users = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        current_user_permission = ProjectPermission.objects.filter(
            project=project,
            user=request.user
        ).first().permission

        users = project.users.exclude(
            id=request.user.id
        ).exclude(
            id=project.creator.id
        )

        filtered_users = []
        for user in users:
            user_permission = ProjectPermission.PERMISSION_LEVELS.get(
                project.permissions.filter(user=user).first().permission
            )
            if user_permission is not None and user_permission < ProjectPermission.PERMISSION_LEVELS.get(current_user_permission):
                filtered_users.append((user.id, user.username))

        self.fields['selected_users'].choices = filtered_users

class AddProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

class AddTaskForm(forms.ModelForm):
    def __init__(self, project_id, *args, **kwargs):
        project = Project.objects.get(id=project_id)
        super(AddTaskForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(id=project_id) # For security reason, this line prevents users from seeing other users' projects
        self.fields['project'].initial = project_id
        self.fields['project'].disabled = True
        self.fields['users'].queryset = project.users.all()

    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'start_datetime': DateTimePickerInput(
                options={
                    "format": "DD-MM-YYYY HH:mm",
                    "useCurrent": False,
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                    "allowInputToggle": True,
                },
                attrs={
                    'class': 'datepicker form-control',
                    'autocomplete': 'off'
                },
            ),
            'end_datetime': DateTimePickerInput(
                range_from="start_datetime",
                options={
                    "format": "DD-MM-YYYY HH:mm",
                    "useCurrent": False,
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                    "allowInputToggle": True,
                },
                attrs={
                    'class': 'datepicker form-control',
                    'autocomplete': 'off'
                },
            ),
            'status': forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'users': forms.CheckboxSelectMultiple(),
        }

class ChangeTaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}),
        }

class ModifyTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')  # Remove 'project' from kwargs
        super().__init__(*args, **kwargs)
        
        # Restrict choices for 'users' field to project users
        self.fields['users'].queryset = project.users.all()
        
    class Meta:
        model = Task
        fields = ['name', 'description', 'start_datetime', 'end_datetime', 'status', 'users']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'start_datetime': DateTimePickerInput(
                options={
                    "format": "DD-MM-YYYY HH:mm",
                    "useCurrent": False,
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                    "allowInputToggle": True,
                },
                attrs={
                    'class': 'datepicker form-control',
                    'autocomplete': 'off'
                },
            ),
            'end_datetime': DateTimePickerInput(
                range_from="start_datetime",
                options={
                    "format": "DD-MM-YYYY HH:mm",
                    "useCurrent": False,
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                    "allowInputToggle": True,
                },
                attrs={
                    'class': 'datepicker form-control',
                    'autocomplete': 'off'
                },
            ),
            'status': forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'users': forms.CheckboxSelectMultiple(),
        }