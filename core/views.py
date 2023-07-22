from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseRedirect
import os

from .models import Project, Task, ProjectPermission, UserProfile, File
from .forms import AddTaskForm, AddProjectForm, ChangeTaskStatusForm, BulkModifyPermissionForm, BulkRemoveUserForm, ModifyTaskForm, UserProfileForm

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    return render(request, "core/index.html")

def myprojects(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    created_projects = request.user.created_projects.all()
    joined_projects = request.user.joined_projects.exclude(creator=request.user)

    return render(request, "core/myprojects.html", {
        "created_projects": created_projects,
        "joined_projects": joined_projects
    })

def project(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all()

    return render(request, "core/project.html", {
        "project": project,
        "tasks": tasks,
    })

def addproject(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    creator = request.user
    if request.method == "POST":
        form = AddProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = creator
            project.save()
            return redirect(reverse("core:myprojects"))

    else:
        form = AddProjectForm()

    return render(request, "core/addproject.html", {
        "form":form,
    })

def deleteproject(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.delete_project()
        return redirect(reverse("core:myprojects"))
    
    return render(request, "core/deleteproject.html", {
        "project":project
    })

def joinproject(request, invite_code):
    if not request.user.is_authenticated:
        return redirect(reverse("account_login"))
    
    project = get_object_or_404(Project, invite_code=invite_code)
    user = request.user
    project.addUser(user)
    return redirect('core:project', project_id=project.id)

def edit_user_profile(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("account_login"))
    
    project = Project.objects.get(id=project_id)
    user_profile = get_object_or_404(UserProfile, user=request.user, project_id=project_id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('core:project', project_id=project_id)
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'form': form,
        'user_profile': user_profile,
        "project": project,
    }

    return render(request, 'core/edit_user_profile.html', context)

def allusers(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    users = project.users.all()

    return render(request, "core/allusers.html", {
        "project": project,
        "users": users,
    })

def addtask(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    if request.method == "POST":
        form = AddTaskForm(project_id, request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()

            # Associate selected users with the task
            selected_users = form.cleaned_data['users']
            task.users.set(selected_users)

            # Handle multiple files
            new_files = request.FILES.getlist('new_files')
            for uploaded_file in new_files:
                file_instance = File(file=uploaded_file, project=project, task=task)
                file_instance.save()

            # Save the task with associated users and files
            form.save_m2m()

            return redirect(reverse("core:project", args=(project.id,)))

    else:
        form = AddTaskForm(project_id)

    return render(request, "core/addtask.html", {
        "form": form,
        "project": project
    })

def taskproperties(request, project_id, task_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    task = Task.objects.get(id=task_id)
    return render(request, "core/taskproperties.html", {
        "project": project,
        "task": task
    })

def changetaskstatus(request, project_id, task_id):
    project = Project.objects.get(id=project_id)
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        form = ChangeTaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse("core:project", args=(project_id,)))
    else:
        form = ChangeTaskStatusForm(instance=task)

    return render(request, "core/changetaskstatus.html", {
        "project": project,
        "form": form,
        "task": task
    })

def modifytask(request, project_id, task_id):
    task = get_object_or_404(Task, id=task_id, project_id=project_id)
    project = task.project

    if request.method == "POST":
        form = ModifyTaskForm(request.POST, request.FILES, instance=task, project=project)
        if form.is_valid():
            task = form.save()
            
            files_to_delete = form.cleaned_data['files_to_delete']

            if files_to_delete:
                # return render(request, 'core/confirm_file_deletion.html', {
                #     'files_to_delete': files_to_delete,
                #     'project': project
                # })
                for file in files_to_delete:
                    file.delete()
                return redirect(reverse("core:project", args=(project_id,)))

            files = request.FILES.getlist('new_files')
            for file in files:
                File.objects.create(task=task, file=file)

            return redirect(reverse("core:project", args=(project_id,)))
    else:
        form = ModifyTaskForm(instance=task, project=project)

    return render(request, 'core/modifytask.html', {
        'form': form,
        'project': project,
        'task': task
    })

def deletetask(request, project_id, task_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = get_object_or_404(Project, id=project_id)
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete_task()
        return redirect(reverse("core:project", args=(project.id,)))
    
    return render(request, "core/deletetask.html", {
        "project":project,
        "task":task
    })

def user_management(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = get_object_or_404(Project, id=project_id)
    project_permission = ProjectPermission.objects.filter(project=project, user=request.user).first()
    users = project.users.all()

    if request.method == "POST":
        form_modify_permissions = BulkModifyPermissionForm(request.POST, project=project, request=request)
        form_delete_users = BulkRemoveUserForm(request.POST, project=project, request=request)

        if form_modify_permissions.is_valid():
            new_permission = form_modify_permissions.cleaned_data['new_permission']
            selected_users = form_modify_permissions.cleaned_data['selected_users']

            for user_id in selected_users:
                user = User.objects.get(id=user_id)
                project.updatePermission(user, new_permission)

            messages.success(request, "Permissions updated successfully.")
            return redirect('core:project', project_id=project.id)
        
        if form_delete_users.is_valid():
            selected_users = form_delete_users.cleaned_data['selected_users']

            for user_id in selected_users:
                user = User.objects.get(id=user_id)
                project.removeUser(user)

            messages.success(request, "Users removed successfully.")
            return redirect('core:project', project_id=project.id)
    else:
        form_modify_permissions = BulkModifyPermissionForm(project=project, request=request)
        form_delete_users = BulkRemoveUserForm(project=project, request=request)

    return render(request, "core/usermanagement.html", {
        "project": project,
        "users": users,
        "form_modify_permissions": form_modify_permissions,
        "form_delete_users": form_delete_users,
    })

def project_management(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))
    
    project = get_object_or_404(Project, id=project_id)

    if not ProjectPermission.objects.filter(project=project, user=request.user).first().has_permission('delete_project'):
        return redirect(reverse("core:project", args=(project.id,)))
                        
    return render(request, "core/projectmanagement.html", {
        "project": project,
    })

def update_project_name(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        new_name = request.POST.get("project_name")
        project.name = new_name
        project.save()

    return redirect(reverse("core:project_management", args=(project.id,)))