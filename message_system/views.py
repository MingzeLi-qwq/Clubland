from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
import json

def message_dashboard(request):
    return render(request, 'messages/message_dashboard.html')

@login_required
def get_user_messages(request):
    user = request.user
    messages = Message.objects.filter(receiver=user).order_by('timestamp')
    
    data = [
        {
            "sender": msg.sender.username,
            "text": msg.text,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in messages
    ]
    return JsonResponse({"messages": data})

@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        sender = request.user
        receiver_username = data.get("receiver")
        text = data.get("text")

        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        message = Message.objects.create(sender=sender, receiver=receiver, text=text)
        return JsonResponse({"message": "Message sent", "id": message.id})
    
def search_users(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(username__icontains=query).values('username') if query else []
    return JsonResponse({"users": list(users)})