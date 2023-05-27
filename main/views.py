from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "main/index.html")
    return render(request, "main/index.html")