from django.shortcuts import render
from django.http import JsonResponse
from .models import Message
from django.contrib.auth import get_user_model
from django.db.models import Q
import json

# Message dashboard view
def message_dashboard(request):
    return render(request, 'messages/message_dashboard.html')

# Get messages
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
def search_users(request):
    query = request.GET.get('q', '')
    User = get_user_model()
    users = User.objects.filter(username__icontains=query)
    
    users_data = [{'id': user.pk, 'username': user.username} for user in users]
    return JsonResponse({'users': users_data})

# Send message
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

        return JsonResponse({'status': 'success'})

# Clear chat
def clear_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            receiver_username = data.get('receiver')

            if not receiver_username:
                return JsonResponse({'status': 'error', 'message': 'Receiver not specified.'})

            try:
                receiver = get_user_model().objects.get(username=receiver_username)
            except get_user_model().DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Receiver not found.'})

            # Delete messages between the current user and the receiver
            Message.objects.filter(sender=request.user, receiver=receiver).delete()
            Message.objects.filter(sender=receiver, receiver=request.user).delete()

            return JsonResponse({'status': 'success', 'message': f'Chat with {receiver_username} cleared.'})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
