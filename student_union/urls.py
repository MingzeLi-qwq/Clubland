"""
URL configuration for student_union project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tutorials.views import views
from django.http import HttpResponse


def student_groups(request):
    return HttpResponse("This is the Student Groups page.")

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('student-groups/', student_groups, name='student_groups'),
    path('accounts/', include('django.contrib.auth.urls')),
]
