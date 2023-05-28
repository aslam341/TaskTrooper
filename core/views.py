from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Project, Task
from .forms import AddTaskForm, AddProjectForm

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
            task = form.save()
            return redirect(reverse("core:myprojects"))

    else:
        form = AddProjectForm()

    return render(request, "core/addproject.html", {
        "form":form,
    })

def addtask(request, project_id):
    if not request.user.is_authenticated:
        return redirect(reverse("main:home"))

    project = Project.objects.get(id=project_id)
    if request.method == "POST":
        form = AddTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect(reverse("core:project", args=(project.id,)))

    else:
        form = AddTaskForm()

    return render(request, "core/addtask.html", {
        "form":form,
        "project":project
    })