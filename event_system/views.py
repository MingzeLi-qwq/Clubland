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
from user_system.models import User

def events_home(request):
    return render(request, 'events.html')

"""This method checks if an Event name already exists, ignoring case and spaces"""
def isSameEventNameExist(name):
    """Check if event name exists (case-insensitive and ignoring spaces)"""
    normalized_name = ''.join(name.split()).lower()
    events = Event.objects.all()
    for event in events:
        normalized_event_name = ''.join(event.name.split()).lower()
        if normalized_name == normalized_event_name:
            return True
    return False

"""------------------------------------------- Event List and Detail Page Rendering Section -----------------------------------------------------"""
class EventListView(ListView):
    """Render event list on events page"""
    model = Event
    template_name = 'events.html'
    context_object_name = "events" 
    paginate_by = 9
    ordering = ["-start_time"] 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.GET
        
        # Combine search conditions
        filters = Q()

        # Keyword search (name, location, description)
        if search := params.get('search'):
            filters &= Q(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Time filter
        now = timezone.now()
        if date_filter := params.get('date'):
            if date_filter == 'upcoming':
                filters &= Q(start_time__gte=now)
            elif date_filter == 'past':
                filters &= Q(end_time__lt=now)

       # Custom time range
        if start_date := params.get('start_date'):
            filters &= Q(start_time__gte=start_date)
        if end_date := params.get('end_date'):
            filters &= Q(start_time__lte=end_date)  

        # Category filter
        if (category := params.get('category')) and category != 'all':
            filters &= Q(categories__name=category)    

        # 俱乐部过滤
        if (club_id := params.get('club')) and club_id != 'all':
            filters &= Q(club__club_id=club_id)

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
            'current_club': params.get('club', 'all'),
            'categories': Category.objects.all(),
            'all_clubs': Club.objects.all(),  # 添加所有俱乐部到上下文
        })
        return context

def event_detail(request, pk):
    """Event detail page"""
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
    """Handle RSVP status toggle"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    event = get_object_or_404(Event, pk=pk)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)

    # Toggle status
    rsvp.status = not rsvp.status if not created else True
    rsvp.save()

    return JsonResponse({
        'status': 'success',
        'new_status': rsvp.status,
        'message': 'RSVP status updated'
    })
"""------------------------------------------- Above section handles Event list and detail page rendering -----------------------------------------------------"""


"""-------------------------------------------------- Event-specific Operations Section -------------------------------------------------"""
"""Remove RSVP"""
class RemoveRSVPView(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id, rsvp_id):
        rsvp = get_object_or_404(RSVP, pk=rsvp_id)
        rsvp.delete()
        messages.success(request, f"RSVP for {rsvp.user.get_full_name} has been removed")
        return redirect('club_manager_event_RSVPs', club_id=club_id, event_id=event_id)
    
"""Create new event"""
class CreateEventView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        categories = Category.objects.all()

        template_path = 'admin_panel/admin_panel_club/create_event.html' \
            if request.user.account_type == User.ACCOUNT_TYPE_ADMIN \
            else 'club_manager/create_event.html'

        return render(request, template_path, {
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
        if request.user.account_type == User.ACCOUNT_TYPE_ADMIN:
            return redirect('admin_panel_club_events', club_id=club_id)
        else:
            return redirect('club_manager_events', club_id=club_id)
    

class DeleteEvent(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, event_id, club_id):
        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_events'
        else:
            redirect_url = 'club_manager_events'

        if request.session.get('password_verified'):
            del request.session['password_verified']
            event = get_object_or_404(Event, id=event_id)
            event_name = event.name
            event.delete()
            messages.success(request, f"Event '{event_name}' has been deleted")
            return redirect(redirect_url, club_id=club_id)
        else:
            return redirect('verify_admin_password')

    def post(self, request, event_id, club_id):
        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_event_general'
        else:
            redirect_url = 'club_manager_event_general'

        if not request.session.get('password_verified'):
            request.session['return_url'] = reverse(redirect_url, kwargs={'club_id': club_id, 'event_id':event_id})
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
            redirect_url = 'admin_panel_club_event_general'
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

        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_event_general'
        else:
            redirect_url = 'club_manager_event_general'

        # Check if the new description is the same as the old one
        if new_description == event.description:
            messages.error(request, "The new description cannot be the same as the old one.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        # Handling of empty descriptions
        if not new_description:
            messages.error(request, "Event Description cannot be empty.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        event.description = new_description
        event.save()
        messages.success(request, "Event description updated successfully.")
        
        return redirect(redirect_url, club_id=club_id, event_id=event_id)

"""Update event time"""
class UpdateEventTime(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, id=event_id, club=club)
        
        start_time = request.POST.get('event_start_time')
        end_time = request.POST.get('event_end_time')

        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_event_general'
        else:
            redirect_url = 'club_manager_event_general'

        if not start_time or not end_time:
            messages.error(request, "Both start and end times are required.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        start_time = timezone.make_aware(timezone.datetime.strptime(start_time, "%Y-%m-%dT%H:%M"))
        end_time = timezone.make_aware(timezone.datetime.strptime(end_time, "%Y-%m-%dT%H:%M"))

        if end_time <= start_time:
            messages.error(request, "End time must be after start time.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        if start_time < timezone.now():
            messages.error(request, "Start time cannot be in the past.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        event.start_time = start_time
        event.end_time = end_time
        event.save()

        messages.success(request, "Event time updated successfully.")
        return redirect(redirect_url, club_id=club_id, event_id=event_id)


"""Update event location"""
class UpdateEventLocation(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, id=event_id, club=club)
        new_location = request.POST.get('event_location', '').strip()

        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_event_general'
        else:
            redirect_url = 'club_manager_event_general'

        if not new_location:
            messages.error(request, "Event location cannot be empty.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)
            
        if new_location == event.location:
            messages.error(request, "The new location cannot be the same as the current one.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)
            
        if Event.objects.filter(club=club, location=new_location).exclude(id=event_id).exists():
            messages.error(request, "Another event already has this location.")
            return redirect(redirect_url, club_id=club_id, event_id=event_id)

        event.location = new_location
        event.save()
        messages.success(request, "Event location updated successfully.")
        return redirect(redirect_url, club_id=club_id, event_id=event_id)

"""Update event event category"""
class UpdateEventCategory(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, event_id):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, id=event_id, club=club)
        selected_categories = request.POST.getlist('categories')
        new_category_name = request.POST.get('new_category', '').strip()

        # 如果访问此view的请求是来自admin panel的, 重定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_event_general'
        else:
            redirect_url = 'club_manager_event_general'

        # 恢复新分类创建逻辑
        if new_category_name:
            if Category.objects.filter(name__iexact=new_category_name).exists():
                messages.warning(request, f"Category '{new_category_name}' already exists")
            else:
                new_category = Category.objects.create(name=new_category_name)
                selected_categories.append(str(new_category.id))
        
        event.categories.set(selected_categories)
        messages.success(request, "Event categories updated successfully")
        return redirect(redirect_url, club_id=club_id, event_id=event_id)

"""--------------------------------------------------以上部分负责针对单个event的相关操作-------------------------------------------------"""


def club_details(request, club_id):
    club = get_object_or_404(Club, pk=club_id)

    # 比如拿该俱乐部最近的活动，不加时间过滤：
    recent_events = Event.objects.filter(club=club).order_by('-start_time')[:3]

    # ... 只想要未来活动，还要加上 start_time__gte=timezone.now() ...
    # recent_events = Event.objects.filter(
    #     club=club,
    #     start_time__gte=timezone.now()
    # ).order_by('start_time')[:3]

    context = {
        'club': club,
        'recent_events': recent_events,
        # 其它上下文...
    }
    return render(request, 'club_details.html', context)


class SearchRSVPCandidatesView(View):
    """搜索可添加为RSVP的用户"""
    def get(self, request, *args, **kwargs):
        club_id = request.GET.get('club_id')
        event_id = request.GET.get('event_id')
        query = request.GET.get('q', '')
        

        # Get users who haven't registered yet
        existing_rsvps = RSVP.objects.filter(event_id=event_id).values_list('user_id', flat=True)
        
        candidates = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            account_type=User.ACCOUNT_TYPE_USER
            )
        # Exclude users who have already signed up
        if event_id:
            event = get_object_or_404(Event, pk=event_id)
            candidates = candidates.exclude(rsvp__event=event)
        
        results = [{
            'username': u.username,
            'email': u.email,
            'full_name': f"{u.first_name} {u.last_name}",
        } for u in candidates]
        
        return JsonResponse(results, safe=False)

"""Add RSVP record"""
class AddRSVPView(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    """Add RSVP record"""
    def post(self, request, club_id, event_id, username):
        try:
            user = User.objects.get(username=username)
            event = Event.objects.get(id=event_id)
            
            # Check if already exists
            if RSVP.objects.filter(user=user, event=event).exists():
                return JsonResponse({'detail': 'User already has RSVP'}, status=400)
            
            # Create RSVP
            RSVP.objects.create(
                user=user,
                event=event,
                status=True
            )
            return JsonResponse({
                'detail': f'{user.get_full_name} added to attendees',
                'status': 'success'
            })
            
        except User.DoesNotExist:
            return JsonResponse({'detail': 'User not found'}, status=404)
        except Event.DoesNotExist:
            return JsonResponse({'detail': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=500)


"""-------------------------------------------------- Above section handles Event-specific operations -------------------------------------------------"""


def club_details(request, club_id):
    club = get_object_or_404(Club, pk=club_id)

    # Get recent events for this club without time filter
    recent_events = Event.objects.filter(club=club).order_by('-start_time')[:3]

    # To get only future events, add start_time__gte=timezone.now()
    # recent_events = Event.objects.filter(
    #     club=club,
    #     start_time__gte=timezone.now()
    # ).order_by('start_time')[:3]

    context = {
        'club': club,
        'recent_events': recent_events,
        # Other context...
    }
    return render(request, 'club_details.html', context)

