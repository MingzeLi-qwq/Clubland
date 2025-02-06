from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from user_system.forms import LoginForm, SignUpForm
from user_system.helpers.mixins import UserTypeRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin


def home(request):
    """Display the application's start/home screen."""
    return render(request, 'shared/home.html')




class SignUpView(View):
    template_name = "user_system/sign_up.html"

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        else:
            return render(request, self.template_name, {"form": form})

class LogInView(View):
    template_name = "user_system/log_in.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = AuthenticationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
        return render(request, self.template_name, {"form": form})

def LogOutView(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')


# def societies(request):
#     """社团列表视图"""
#     return render(request, 'shared/societies.html')

def news(request):
    """新闻视图"""
    return render(request, 'shared/news.html')

def events(request):
    """活动视图"""
    return render(request, 'shared/events.html')

class DashboardView(LoginRequiredMixin, UserTypeRequiredMixin, TemplateView):
    template_name = "user_system/dashboard.html"
    allowed_types = ['User']