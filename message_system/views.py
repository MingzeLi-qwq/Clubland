from django.shortcuts import render
from django.http import JsonResponse
from .models import Message  # 导入 Message 模型
from django.contrib.auth import get_user_model  # 使用 get_user_model 获取当前配置的用户模型

# 示例视图函数
def message_dashboard(request):
    # 处理请求并返回渲染的模板
    return render(request, 'messages/message_dashboard.html')  # 假设您有一个模板 'dashboard.html'

# 获取所有消息
def get_messages(request):
    messages = Message.objects.all()
    messages_data = [{
        'sender': message.sender.username,
        'text': message.text,
    } for message in messages]
    return JsonResponse({'messages': messages_data})

# 搜索用户
def search_users(request):
    query = request.GET.get('q', '')
    User = get_user_model()
    users = User.objects.filter(username__icontains=query)
    
    # 使用 pk 作为唯一标识符
    users_data = [{'id': user.pk, 'username': user.username} for user in users]
    
    return JsonResponse({'users': users_data})


# 发送消息
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        text = request.POST.get('text')
        # 获取当前用户作为发送者
        sender = request.user
        try:
            # 查找接收者用户
            receiver = get_user_model().objects.get(username=receiver_username)
        except get_user_model().DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Receiver not found'})

        # 创建并保存消息
        Message.objects.create(sender=sender, receiver=receiver, text=text)
        return JsonResponse({'status': 'success'})
