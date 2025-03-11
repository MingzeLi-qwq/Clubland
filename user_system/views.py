from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from user_system.forms import LoginForm, SignUpForm
from user_system.helpers.mixins import UserTypeRequiredMixin
from club_system.helpers.mixins import ClubMemberRequiredMixin, ClubExistsRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from club_system.models import Membership, NewClubRequest, Club
from event_system.models import Event
from news_system.models import News  # 添加导入News模型
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.db.models import Q
import re
from bs4 import BeautifulSoup
from django.utils.html import strip_tags



def home(request):
    """优化后的首页视图，包含缓存和查询优化"""
    if request.user.is_authenticated:
        return redirect('Mine')

    # 使用select_related优化关联查询
    upcoming_events = Event.objects.filter(
        start_time__gte=timezone.now()
    ).select_related('club').order_by('start_time')

    # 直接获取最新社团
    new_clubs = Club.objects.select_related('creator').order_by('-created_at')[:4]

    # 简化新闻数据处理
    news_items = News.objects.select_related('author').order_by('-created_at')[:3]
    simplified_news = [
        {
            'id': n.id,
            'title': n.title,

            'cover': n.cover_url,  # 假设模型已有封面图字段
            'url': reverse('news_detail', args=[n.id])
        }
        for n in news_items
    ]

    # 简单分页（移除AJAX支持）
    paginator = Paginator(upcoming_events, 3)
    page_number = request.GET.get('page')
    try:
        events_page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        events_page = paginator.page(1)

    return render(request, 'shared/home.html', {
        'events': events_page,
        'new_clubs': new_clubs,
        'recent_news': simplified_news,
    })




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

def events(request):
    """活动视图"""
    return render(request, 'shared/events.html')
    

"""此方法用来处理来自User Dashboard的密码修改请求"""
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 防止用户被登出
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard_personal_information')  # 这里要确保你的 URL 名称正确
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'user_system/dashboard/personal_information.html', {'form': form})


"""以下内容负责渲染Personal Dashboard"""
class DashboardPersonalInformation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_system/dashboard/personal_information.html')

class DashboardMyClub(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']

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

class DashboardMyRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, *args, **kwargs):
        return render(request, 'user_system/dashboard/requests/my_requests.html')


"""以下内容用来处理Personal Dashboard查看New Club Requests的请求"""
class NewClubRequestsView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request):
        pending_requests = NewClubRequest.objects.filter(creator=request.user, status=NewClubRequest.STATUS_PENDING)
        approved_requests = NewClubRequest.objects.filter(creator=request.user, status=NewClubRequest.STATUS_APPROVED)
        rejected_requests = NewClubRequest.objects.filter(creator=request.user, status=NewClubRequest.STATUS_REJECTED)

        context = {
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
        }
        return render(request, 'user_system/dashboard/requests/new_club_requests.html', context)
    
"""以下内容用来渲染personal dashboard查看club memebership detail的请求"""
class ClubMembershipDetail(LoginRequiredMixin, ClubExistsRequiredMixin, UserTypeRequiredMixin, ClubMemberRequiredMixin, View):
    allowed_types = ['User']
    
    def get(self, request, club_id):
        try:
            # 尝试获取当前用户在指定俱乐部的会员资格
            membership = Membership.objects.get(user=request.user, club_id=club_id)
        except Membership.DoesNotExist:
            # 如果会员资格不存在，添加错误消息并重定向
            messages.error(request, "The specified membership does not exist.")
            return redirect('dashboard_my_club')

        # 如果会员资格存在，渲染详情页面
        context = {
            'membership': membership
        }
        return render(request, 'user_system/dashboard/my_club_detail.html', context)

@login_required
def Mine(request):
    """Mine view"""
    # Get user's clubs through memberships
    user_clubs = Club.objects.filter(membership__user=request.user)
    
    # Get user's upcoming events (both club events and RSVPed events)
    upcoming_events = Event.objects.filter(
        Q(club__in=user_clubs) |  # Events from user's clubs
        Q(rsvp__user=request.user),  # Events user has RSVPed to
        start_time__gte=timezone.now()
    ).distinct().order_by('start_time')
    
    return render(request, 'user_system/mine.html', {
        'clubs': user_clubs,
        'events': upcoming_events,
    })

def about_us(request):
    """关于我们页面"""
    return render(request, 'shared/about_us.html')




