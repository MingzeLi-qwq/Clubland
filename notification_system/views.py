from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Notification

def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notification_system/notifications.html', {'notifications': notifications})

def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, 'notification_system/notification_detail.html', {'notification': notification})

def base_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    unread_notifications_count = notifications.count()
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
