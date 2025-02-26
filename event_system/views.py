from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import RSVP, Category, Event
from django.views.generic import ListView
from django.db.models import Q 
from django.utils import timezone 
from datetime import timedelta
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from club_system.helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, ClubManagerRequiredMixin
from django.views import View
from club_system.models import Club
from django.contrib import messages
from django.urls import reverse

def events_home(request):
    return render(request, 'events.html')

"""此方法用于检查Event name是否重复, 更重要的是忽略了大小写和空格"""
def isSameEventNameExist(name):
    normalized_name = ''.join(name.split()).lower()
    events = Event.objects.all()
    for event in events:
        normalized_event_name = ''.join(event.name.split()).lower()
        if normalized_name == normalized_event_name:
            return True
    return False

"""-------------------------------------------以下部分在Event页面渲染event列表和event详情页面-----------------------------------------------------"""
class EventListView(ListView):
    """在event页面渲染event列表"""
    model = Event
    template_name = 'events.html'
    context_object_name = "events" 
    paginate_by = 9
    ordering = ["-start_time"] 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.GET
        
        # 组合搜索条件
        filters = Q()

        # 关键词搜索（名称、地点、描述）
        if search := params.get('search'):
            filters &= Q(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        
        # 时间过滤
        now = timezone.now()
        if date_filter := params.get('date'):
            if date_filter == 'upcoming':
                filters &= Q(start_time__gte=now)
            elif date_filter == 'past':
                filters &= Q(end_time__lt=now)
       # 自定义时间
        if start_date := params.get('start_date'):
            filters &= Q(start_time__gte=start_date)
        if end_date := params.get('end_date'):
            filters &= Q(start_time__lte=end_date)  

        # 分类过滤
        if (category := params.get('category')) and category != 'all':
            filters &= Q(categories__name=category)    

        return queryset.filter(filters).distinct().order_by('start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET

        context.update({
            'current_search': params.get('search', ''),
            'current_date_filter': params.get('date', ''),
            'current_category': params.get('category', 'all'),
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', ''),
            'categories': Category.objects.all(),
        })
        return context

def event_detail(request, pk):
    """event详情页面"""
    event = get_object_or_404(Event, pk=pk)
    user_rsvp = RSVP.objects.filter(
        user=request.user, 
        event=event
    ).first() if request.user.is_authenticated else None
    club = event.club

    return render(request, 'event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp,
        'club':club,
    })

@login_required
def rsvp_toggle(request, pk):
    """ 处理 RSVP 状态切换 """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    event = get_object_or_404(Event, pk=pk)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)

    # 切换状态
    rsvp.status = not rsvp.status if not created else True
    rsvp.save()

    return JsonResponse({
        'status': 'success',
        'new_status': rsvp.status,
        'message': 'RSVP status updated'
    })
"""-------------------------------------------以上部分在Event页面渲染event列表和event详情页面-----------------------------------------------------"""


"""--------------------------------------------------以下部分负责针对单个event的相关操作-------------------------------------------------"""
"""Remove RSVP / 移除RSVP"""
class RemoveRSVPView(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id, rsvp_id):
        rsvp = get_object_or_404(RSVP, pk=rsvp_id)
        rsvp.delete()
        messages.success(request, f"RSVP for {rsvp.user.get_full_name} has been removed")
        return redirect('club_manager_event_RSVPs', club_id=club_id, event_id=event_id)
    
"""Create new even / 创建新的event"""
class CreateEventView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        categories = Category.objects.all()
        # 渲染活动创建表单页面
        return render(request, 'club_manager/create_event.html', {
            'club_id': club_id, 
            'club': club,
            'categories': categories,
            })

    def post(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        start_time = request.POST.get('start_time', '').strip()  # 注意时间格式校验
        end_time = request.POST.get('end_time', '').strip()  # 注意时间格式校验
        location = request.POST.get('location', '').strip()

        # 获取选择的 category PKs
        category_pks = request.POST.getlist('categories')

        # 简单校验
        if not name or not start_time or not end_time or not location:
            messages.error(request, "Title, time and place are required")
            return redirect('create_event', club_id=club_id)

        # 检查事件名称是否重复
        if isSameEventNameExist(name):
            messages.error(request, "Event with the same name already exists")
            return redirect('create_event', club_id=club_id)

        # 创建新的活动
        event = Event.objects.create(
            club=club,
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
        )

        # 添加选择的 categories
        if category_pks:
            categories = Category.objects.filter(pk__in=category_pks)
            event.categories.add(*categories)

        messages.success(request, "Event created successfully!")
        # 创建后跳转到编辑页面，便于 manager 进一步完善活动内容
        return redirect('club_manager_events', club_id=club_id)
    

class DeleteEvent(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, event_id, club_id):
        if request.session.get('password_verified'):
            del request.session['password_verified']
            event = get_object_or_404(Event, id=event_id)
            event_name = event.name
            event.delete()
            messages.success(request, f"Event '{event_name}' has been deleted")
            return redirect('club_manager_events', club_id=club_id)
        else:
            return redirect('verify_admin_password')

    def post(self, request, event_id, club_id):
        if not request.session.get('password_verified'):
            request.session['return_url'] = reverse('club_manager_event_general', kwargs={'club_id': club_id, 'event_id':event_id})
            request.session['pending_action'] = 'delete_event'
            request.session['club_id'] = club_id
            request.session['event_id'] = event_id
            return redirect('verify_admin_password')
        else:
            return self.get(request, event_id, club_id)

    
"""Changing the name for Event"""
class UpdateEventName(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, id=event_id, club=club)
        new_name = request.POST.get('event_name', '').strip()

        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_event_general'
        else:
            redirect_url = 'club_manager_event_general'

        if new_name == event.name:
            messages.error(request, "The new name cannot duplicate the old name.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        if not new_name:
            messages.error(request, "Event name cannot be empty.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)
        
        if isSameEventNameExist(new_name):
            messages.error(request, "There's already an Event with the same name.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)
            
        try:
            event.name = new_name
            event.save()
            messages.success(request, "Event name updated successfully.")
        except IntegrityError:
            messages.error(request, "This event name does not match the specification.")
        
        return redirect(redirect_url, club_id=club_id, event_id=event_id)

"""Change Event Description"""
class UpdateEventDescription(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, id=event_id, club=club)
        new_description = request.POST.get('event_description', '').strip()

        # Check if the new description is the same as the old one
        if new_description == event.description:
            messages.error(request, "The new description cannot be the same as the old one.")
            return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)

        # Handling of empty descriptions
        if not new_description:
            messages.error(request, "Event Description cannot be empty.")
            return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)

        event.description = new_description
        event.save()
        messages.success(request, "Event description updated successfully.")
        
        return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)

"""Update event time"""
class UpdateEventTime(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, id=event_id, club=club)
        
        start_time = request.POST.get('event_start_time')
        end_time = request.POST.get('event_end_time')

        if not start_time or not end_time:
            messages.error(request, "Both start and end times are required.")
            return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)

        start_time = timezone.make_aware(timezone.datetime.strptime(start_time, "%Y-%m-%dT%H:%M"))
        end_time = timezone.make_aware(timezone.datetime.strptime(end_time, "%Y-%m-%dT%H:%M"))

        if end_time <= start_time:
            messages.error(request, "End time must be after start time.")
            return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)

        if start_time < timezone.now():
            messages.error(request, "Start time cannot be in the past.")
            return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)

        event.start_time = start_time
        event.end_time = end_time
        event.save()

        messages.success(request, "Event time updated successfully.")
        return redirect('club_manager_event_general', club_id=club_id, event_id=event_id)


"""--------------------------------------------------以上部分负责针对单个event的相关操作-------------------------------------------------"""