from django.shortcuts import render
from clubs.models import ClubRequest
from clubs.models import Membership
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect

@login_required
def user_center_view(request):
    return render(request, 'users/user_center.html')


@login_required
def club_requests_view(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Only admins can access this page.")
    club_requests = ClubRequest.objects.filter(status='pending')
    return render(request, 'users/club_requests.html', {'club_requests': club_requests})


@login_required
def my_clubs_view(request):
    memberships = Membership.objects.filter(user=request.user)
    return render(request, 'users/my_clubs.html', {'memberships': memberships})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 自动登录
            return redirect('home')  # 跳转到主页
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
