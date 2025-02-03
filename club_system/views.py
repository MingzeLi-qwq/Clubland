from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Club
from .helpers.mixins import ClubExistsRequiredMixin

def clubs(request):
    clubs = Club.objects.all()
    return render(request, 'clubs.html', {'clubs': clubs})


class ClubDetailView(ClubExistsRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, 'club_detail.html', {'club': club})