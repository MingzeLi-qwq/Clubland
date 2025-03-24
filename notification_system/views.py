from django.shortcuts import render, get_object_or_404
from .models import Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def notification_list(request):
    '''Retrieve all notifications for the current user'''
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notification_system/notifications.html', {'notifications': notifications})

def notification_detail(request, notification_id):
    '''Access a single notification and mark it as read'''
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, 'notification_system/notification_detail.html', {'notification': notification})

def base_notifications(request):
    '''Load unread notifications as global context in base.html'''
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    unread_notifications_count = notifications.count()
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }

def mark_all_as_read(request):
    """Batch mark all unread notifications as read"""
    if request.method == 'POST' and request.user.is_authenticated:
        # Find all unread notifications for the current user
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        updated_count = unread_notifications.count()

        # Mark these notifications as read
        unread_notifications.update(is_read=True)

        return JsonResponse({'status': 'success', 'updated_count': updated_count})
    
    return JsonResponse({'status': 'failure'}, status=400)

@login_required
def delete_notification(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def delete_all_notifications(request):
    """Manually delete all notifications"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)
