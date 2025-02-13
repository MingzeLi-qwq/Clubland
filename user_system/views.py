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
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from club_system.models import Membership


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
    

"""此方法用来处理来自User Dashboard的密码修改请求"""
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')  
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'user_system/change_password.html', {'form': form})


"""以下内容负责渲染Personal Dashboard"""
class DashboardPersonalInformation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_system/dashboard/personal_informations.html')

class DashboardMyClub(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # 获取用户作为管理员的社团
        managed_clubs = Membership.objects.filter(user=user, is_manager=True)
        # 获取用户作为普通成员的社团
        member_clubs = Membership.objects.filter(user=user, is_manager=False)
        
        return render(request, 'user_system/dashboard/my_club.html', {
            'managed_clubs': managed_clubs,
            'member_clubs': member_clubs
    })