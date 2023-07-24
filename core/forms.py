from django import forms
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from phonenumber_field.formfields import PhoneNumberField
from .models import Project, Task, ProjectPermission, UserProfile, File
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from django.core.files.uploadedfile import TemporaryUploadedFile

# Allow bulk file upload
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

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
    new_files = MultipleFileField(required=False)

    def __init__(self, project_id, *args, **kwargs):
        project = Project.objects.get(id=project_id)
        super(AddTaskForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(id=project_id) # For security reason, this line prevents users from seeing other users' projects
        self.fields['project'].initial = project_id
        self.fields['project'].disabled = True
        self.fields['users'].queryset = project.users.all()

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')

        if start_datetime and end_datetime and start_datetime > end_datetime:
            raise ValidationError("Start datetime must be same as or before the end datetime.")
        
    def save(self, commit=True):
        instance = super().save(commit=commit)

        if commit:
            # Save the new_files only when commit is True
            new_files = self.cleaned_data.get('new_files')
            if new_files:
                for uploaded_file in new_files:
                    file_instance = File(file=uploaded_file, project=instance.project, task=instance)
                    file_instance.save()

        return instance

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
    new_files = MultipleFileField(required=False)
    files_to_delete = forms.ModelMultipleChoiceField(
        queryset=File.objects.none(),  # We'll override this queryset later in the __init__ method
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')  # Remove 'project' from kwargs
        super().__init__(*args, **kwargs)
        
        # Restrict choices for 'users' field to project users
        self.fields['users'].queryset = project.users.all()

        # Update queryset for files_to_delete field to display existing task_files
        self.fields['files_to_delete'].queryset = File.objects.filter(task=kwargs['instance'])
        
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

class UserProfileForm(forms.ModelForm):
    display_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Name you want others to see'}),
        required=False
    )

    role = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Developer'}),
        required=False
    )

    phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={'placeholder': '+65 9876 5432'}),
        required=False
    )

    email_address = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'example@gmail.com'}),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['display_name', 'role', 'phone_number', 'email_address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['email_address'].widget.attrs.update({'class': 'form-control'})