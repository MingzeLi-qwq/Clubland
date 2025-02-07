from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Notification

def notification_list(request):
    '''获取当前用户的所有通知'''
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notification_system/notifications.html', {'notifications': notifications})

def notification_detail(request, notification_id):
    '''访问单条通知，并将其标记为已读'''
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, 'notification_system/notification_detail.html', {'notification': notification})

def base_notifications(request):
    '''在 base.html 里使用全局上下文加载未读通知'''
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    unread_notifications_count = notifications.count()
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
