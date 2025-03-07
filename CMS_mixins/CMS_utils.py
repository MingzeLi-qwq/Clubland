import os
import uuid
from datetime import datetime

# 将上传路径函数封装到一个类中
class RTEUploadUtils:
    @staticmethod
    def upload_img_func(instance, filename):
        """
        上传附件时生成文件保存路径，示例格式：attachments/2025/02/18/随机UUID.扩展名
        """
        ext = filename.split('.')[-1]
        new_filename = f"{uuid.uuid4()}.{ext}"
        today = datetime.today().strftime('%Y/%m/%d')
        return os.path.join("attachments", today, new_filename)
    
    @staticmethod
    def delete_associated_images(instance):
        # 若实例中存在 image 字段（并含有文件），则删除该文件
        if hasattr(instance, 'image') and instance.image:
            image_path = instance.image.path
            if os.path.exists(image_path):
                os.remove(image_path)

# 新增 UserFormMixin 封装表单常用方法
class UserFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

def get_paginate_by_request(request, param='per_page', default=10):
    """根据请求参数返回分页大小的通用函数。"""
    per_page = request.GET.get(param)
    if (per_page and per_page.isdigit()):
        return int(per_page)
    return default

def set_club_field(form, user, manage_only=False):
    from django.apps import apps
    Club = apps.get_model("club_system", "Club")
    """
    设置 club 字段的可选范围:
      - 若用户是管理员，则列出所有社团并允许为空。
      - 否则根据 manage_only 决定：只列举可管理的社团或已加入的社团。
    """
    if user and user.is_admin:
        form.fields['club'].queryset = Club.objects.all()
        form.fields['club'].required = False
    else:
        if manage_only:
            form.fields['club'].queryset = Club.objects.filter(
                membership__user=user, membership__is_manager=True
            ).distinct()
        else:
            form.fields['club'].queryset = getattr(user, 'clubs_joined', Club.objects.none())

def set_event_field(form, data, instance, club_field='club', event_field='event'):
    from django.apps import apps
    Event = apps.get_model("event_system", "Event")
    """
    根据所选社团过滤可选活动。
    """
    if data.get(club_field):
        try:
            club_id = int(data.get(club_field))
            form.fields[event_field].queryset = Event.objects.filter(club_id=club_id)
        except (ValueError, TypeError):
            form.fields[event_field].queryset = Event.objects.none()
    elif instance.pk and getattr(instance, club_field):
        form.fields[event_field].queryset = Event.objects.filter(club=getattr(instance, club_field))
    else:
        form.fields[event_field].queryset = Event.objects.none()

