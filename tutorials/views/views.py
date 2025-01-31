# tutorials/views/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')

def signup(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 自动登录
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})

def custom_login(request):
    """用户登录视图"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})
@login_required
def profile(request):
    """用户个人资料视图"""
    return render(request, 'profile.html')

def societies(request):
    """社团列表视图"""
    return render(request, 'societies.html')

def news(request):
    """新闻视图"""
    return render(request, 'news.html')

def events(request):
    """活动视图"""
    return render(request, 'events.html')