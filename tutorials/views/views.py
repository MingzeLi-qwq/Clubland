from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View

def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')