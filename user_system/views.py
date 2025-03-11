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
    """Display the application's start/home screen."""
    if request.user.is_authenticated:
        return redirect('Mine')  # Redirect authenticated users to Mine page
    
    page = request.GET.get('page', 1)
    events_per_page = 3
    
    upcoming_events_list = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')
    
    # 查询最新的社团 - 按照创建时间倒序排列，取最新的4个
    new_clubs = Club.objects.order_by('-club_id')[:4]
    
    # 查询最新的新闻 - 按照创建时间倒序排列，取最新的3条
    news_items = News.objects.order_by('-created_at')[:3]
    
    # 增强新闻数据，添加摘要和图片URL
    enhanced_news = []
    for news in news_items:
        # 从内容中提取第一张图片的URL
        first_image_url = None
        if news.content:
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(news.content, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.has_attr('src'):
                first_image_url = img_tag['src']
        
        # 创建摘要 - 从内容中提取纯文本并截取前100个字符
        summary = ""
        if news.content:
            text_content = strip_tags(news.content)
            summary = text_content[:100] + "..." if len(text_content) > 100 else text_content
        
        enhanced_news.append({
            'id': news.id,
            'title': news.title,
            'summary': summary,
            'first_image_url': first_image_url,
            'created_at': news.created_at,
            'url': f'/news/{news.id}/'  # 假设新闻详情页的URL格式
        })
    
    paginator = Paginator(upcoming_events_list, events_per_page)
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)
    
    # 处理 AJAX 请求
    if request.GET.get('ajax'):
        # 渲染部分模板
        events_html = render_to_string('shared/events_list.html', {'events': events})
        pagination_html = render_to_string('shared/pagination.html', {'events': events})
        
        return JsonResponse({
            'events_html': events_html,
            'pagination_html': pagination_html,
            'current_page': events.number,
            'total_pages': paginator.num_pages,
            'has_next': events.has_next(),
            'has_previous': events.has_previous(),
        })
    
    return render(request, 'shared/home.html', {
        'events': events,
        'new_clubs': new_clubs,
        'recent_news': enhanced_news,
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
        else:
            # 添加错误提示
            messages.error(request, "Invalid username or password.")
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




