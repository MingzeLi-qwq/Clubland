from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Club, Membership, WidgetInstance
from .helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin
from event_system.models import Event
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def clubs(request):
    clubs = Club.objects.all()
    return render(request, 'clubs.html', {'clubs': clubs})

def home(request):
    clubs = Club.objects.all()
    events = Event.objects.all().order_by('-start_time')[:5]  # 显示最新5个活动
    return render(request, 'home.html', {'clubs': clubs, 'events': events})

class ClubDetailView(ClubExistsRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, 'club_detail.html', {'club': club})
    
class RegisterMembershipView(ClubExistsRequiredMixin, NonClubMemberRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        if request.user.is_authenticated:
            Membership.objects.get_or_create(user=request.user, club=club)
            return redirect('club_detail', club_id=club_id)
        else:
            return redirect('login')
        
class CancelMembershipView(ClubExistsRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        if request.user.is_authenticated:
            Membership.objects.filter(user=request.user, club=club).delete()
            return redirect('club_detail', club_id=club_id)
        else:
            return redirect('login')

@login_required
def club_dashboard(request, club_id):
    club = get_object_or_404(Club, club_id=club_id)
    if not Membership.objects.filter(club=club, user=request.user, club__isnull=False).exists():
        return render(request, '403.html', status=403)
    
    return render(request, 'club_website/club_dashboard.html', {
        'club': club,
        'widgets': club.widgets.all(),
        'customization': club.customization,
        'membership': Membership.objects.get(club=club, user=request.user)
    })

class ClubWidgetAPI(View):
    def get(self, request, club_id):
        club = get_object_or_404(Club, club_id=club_id)
        widgets = list(club.widgets.values(
            'widget_type', 'position_x', 'position_y', 'width', 'height', 'config'))
        return JsonResponse({'layout': widgets})

    def post(self, request, club_id):
        club = get_object_or_404(Club, club_id=club_id)
        if not Membership.objects.filter(club=club, user=request.user, is_manager=True).exists():
            return JsonResponse({'status': 'forbidden'}, status=403)
        
        # 清空旧布局
        club.widgets.all().delete()
        
        # 保存新布局
        widgets = request.JSON.get('widgets', [])
        for widget in widgets:
            WidgetInstance.objects.create(
                club=club,
                widget_type=widget['type'],
                position_x=widget['x'],
                position_y=widget['y'],
                width=widget['w'],
                height=widget['h'],
                config=widget.get('config', {})
            )
        return JsonResponse({'status': 'success'})
