from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Project, Task
from .forms import AddTaskForm, AddProjectForm, ChangeTaskStatusForm

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    return render(request, "core/index.html")

def myprojects(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    return render(request, "core/myprojects.html", {
        "projects": request.user.projects.all()
    })

def project(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    tasks = project.tasks.all()
    return render(request, "core/project.html", {
        "project": project,
        "tasks": tasks
    })

def addproject(request):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    user = request.user
    if request.method == "POST":
        form = AddProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = user
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

def addtask(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    if request.method == "POST":
        form = AddTaskForm(project_id, request.POST)
        if form.is_valid():
            task = form.save()
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
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        form = ChangeTaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse("core:project", args=(project_id,)))
    else:
        form = ChangeTaskStatusForm(instance=task)

    return render(request, "core/changetaskstatus.html", {
        "form":form,
        "task":task
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