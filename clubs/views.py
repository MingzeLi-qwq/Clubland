from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Club, News
from .forms import NewsForm
from .forms import EventForm
from clubs.models import Membership

def club_list(request):
    clubs = Club.objects.all()
    return render(request, 'clubs/club_list.html', {'clubs': clubs})


@login_required
def create_news(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    # 确保当前用户是社团团长或管理员
    if request.user != club.leader and request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to create news for this club.")

    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.club = club
            news.created_by = request.user
            news.save()
            return redirect('club_detail', club_id=club.id)  # 重定向到社团详情页
    else:
        form = NewsForm()

    return render(request, 'clubs/create_news.html', {'form': form, 'club': club})


@login_required
def create_event(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    # 确保当前用户是社团团长或管理员
    if request.user != club.leader and request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to create events for this club.")

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            return redirect('club_detail', club_id=club.id)  # 重定向到社团详情页
    else:
        form = EventForm()

    return render(request, 'clubs/create_event.html', {'form': form, 'club': club})


@login_required
def manage_members_view(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.leader:
        return HttpResponseForbidden("You are not allowed to manage this club.")
    members = Membership.objects.filter(club=club)
    return render(request, 'clubs/manage_members.html', {'club': club, 'members': members})
