from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, F

from .models import Project, Task, ProjectPermission
from .forms import AddTaskForm, AddProjectForm, ChangeTaskStatusForm, BulkModifyPermissionForm, BulkRemoveUserForm, ModifyTaskForm

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
        return redirect(reverse("account:login"))
    
    project = get_object_or_404(Project, invite_code=invite_code)
    user = request.user
    project.addUser(user)
    return redirect('core:project', project_id=project.id)

def addtask(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    if request.method == "POST":
        form = AddTaskForm(project_id, request.POST)
        if form.is_valid():
            task = form.save()
            task.save()
            return redirect(reverse("core:project", args=(project.id,)))

    else:
        form = AddTaskForm(project_id)

    return render(request, "core/addtask.html", {
        "form":form,
        "project":project
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
        form = ModifyTaskForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
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