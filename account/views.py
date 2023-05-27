from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import RegisterForm

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("main:home"))
    else:
        form = RegisterForm()

    return render(request, "account/signup.html", {"form":form})
