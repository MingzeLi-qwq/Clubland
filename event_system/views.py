from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event


def event_list(request):
    events = Event.objects.all().order_by('-start_time')
    return render(request, 'event_list.html', {'events': events})


@login_required
def rsvp_event(request, event_name):
    event = get_object_or_404(Event, name=event_name)
    user = request.user

    # 切换用户的参与状态
    if user in event.participants.all():
        event.participants.remove(user)
    else:
        event.participants.add(user)

    return redirect('event_list')

# Create your views here.
