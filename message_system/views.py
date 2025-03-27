from django.shortcuts import render
from django.http import JsonResponse
from .models import Message
from django.contrib.auth import get_user_model
from django.db.models import Q
import json
from django.contrib.auth.decorators import login_required

# Message dashboard view
@login_required
def message_dashboard(request):
    return render(request, 'messages/message_dashboard.html')

# Get messages
@login_required
def get_messages(request):
    receiver = request.GET.get('receiver')
    user = request.user
    
    if receiver:
        messages = Message.objects.filter(
            (Q(sender=user) & Q(receiver__username=receiver)) |
            (Q(receiver=user) & Q(sender__username=receiver))
        ).order_by('timestamp')
    else:
        messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('timestamp')

    data = {
        'messages': [
            {
                'sender': msg.sender.username,
                'receiver': msg.receiver.username,
                'text': msg.text
            }
            for msg in messages
        ]
    }
    return JsonResponse(data)

# Search users
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    User = get_user_model()
    users = User.objects.filter(username__icontains=query)
    
    users_data = [{'id': user.pk, 'username': user.username} for user in users]
    return JsonResponse({'users': users_data})

# Send message
@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        text = request.POST.get('text')

        sender = request.user

        try:
            receiver = get_user_model().objects.get(username=receiver_username)
        except get_user_model().DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Receiver not found'})

        Message.objects.create(sender=sender, receiver=receiver, text=text)

        Notification.objects.create(
            user=receiver,
            title=f"New Message from {sender.username}",
            message=f"You have a new message from {sender.username}. Click 'continue' to check your messages",
            notification_type='general',
            url=reverse('message_dashboard'),
        )

        return JsonResponse({'status': 'success'})

