from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from clubs.models import ClubRequest
from clubs.models import Membership  # 导入 Membership 模型


User = get_user_model()

def register(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 注册成功后自动登录用户
            return redirect('home')  # 跳转到主页或其他页面
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_center_view(request):
    """用户中心视图"""
    return render(request, 'users/user_center.html')


@login_required
def club_requests_view(request):
    """显示所有社团创建请求，仅供管理员访问"""
    if not request.user.is_superuser and request.user.role != 'admin':
        return render(request, '403.html', status=403)  # 返回无权限页面

    club_requests = ClubRequest.objects.all()
    return render(request, 'users/club_requests.html', {'club_requests': club_requests})




@login_required
def my_clubs_view(request):
    """显示用户参加的所有社团"""
    memberships = Membership.objects.filter(user=request.user)
    clubs = [membership.club for membership in memberships]
    return render(request, 'users/my_clubs.html', {'clubs': clubs})
