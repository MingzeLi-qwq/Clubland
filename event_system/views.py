from datetime import timezone
from unicodedata import category
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import RSVP, Category, Event
from django.views.generic import ListView

def home(request):
    upcoming_events = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    featured_events = Event.objects.filter(is_featured=True)[:3]
    return render(request, 'home.html', {
        'upcoming_events': upcoming_events,
        'featured_events': featured_events,
        'categories': category,
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

        # Get filter parameters /获取过滤参数
        search = self.request.GET.get('search')
        date_filter = self.request.GET.get('date')
        category = self.request.GET.get('category')
        
        #Search filter /搜索过滤
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        #time filter /时间过滤
        
        if date_filter == 'upcoming':
            queryset = queryset.filter(start_time__gte=timezone.now())
        elif date_filter == 'past':
            queryset = queryset.filter(end_time__lt=timezone.now())
        if category:
            queryset = queryset.filter(categories__name=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['events'] = Event.objects.all()
        return context

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvp = RSVP.objects.filter(user=request.user, event=event).first() if request.user.is_authenticated else None
    return render(request, 'event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp
    })

@login_required
def rsvp_toggle(request, pk):
    event = get_object_or_404(Event, pk=pk)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
    
    if request.method == 'POST':
        rsvp.status = not rsvp.status
        rsvp.save()
        return JsonResponse({'status': 'success', 'new_status': rsvp.status})
    return JsonResponse({'status': 'error'})
