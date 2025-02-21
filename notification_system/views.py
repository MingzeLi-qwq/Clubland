from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

def mark_all_as_read(request):
    """批量標記所有未讀通知為已讀"""
    if request.method == 'POST' and request.user.is_authenticated:
        # 找到當前用戶的所有未讀通知
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        updated_count = unread_notifications.count()

        # 將這些通知標記為已讀
        unread_notifications.update(is_read=True)

        return JsonResponse({'status': 'success', 'updated_count': updated_count})
    
    return JsonResponse({'status': 'failure'}, status=400)