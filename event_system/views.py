
from unicodedata import category
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import RSVP, Category, Event
from django.views.generic import ListView
from django.db.models import Q 
from django.utils import timezone 
from datetime import timedelta

def home(request):
    # 获取未来30天的精选活动并按开始时间排序
    featured_events = Event.objects.filter(
        is_featured=True,
        start_time__gte=timezone.now() - timedelta(days=1),  
        end_time__gte=timezone.now()
    ).order_by('start_time')[:6]  
    
    upcoming_events = Event.objects.filter(
        start_time__gte=timezone.now()
    ).exclude(id__in=[e.id for e in featured_events])[:5]  # 排除已展示的精选活动
    
    return render(request, 'home.html', {
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'categories': Category.objects.all(),
    })

def events_home(request):
    return render(request, 'events.html')

class EventListView(ListView):
    model = Event
    template_name = 'events.html'
    context_object_name = "events" 
    paginate_by = 10
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

        
        # 精选活动过滤
        if params.get('is_featured'):
            filters &= Q(is_featured=True)

        return queryset.filter(filters).distinct().order_by('start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET
     # 保留搜索参数
        context.update({
            'current_search': params.get('search', ''),
            'current_date_filter': params.get('date', ''),
            'current_category': params.get('category', 'all'),
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', ''),
            'is_featured': params.get('is_featured', False),
            'categories': Category.objects.all(),
        })
        return context

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvp = RSVP.objects.filter(
        user=request.user, 
        event=event
    ).first() if request.user.is_authenticated else None

    return render(request, 'event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp
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

