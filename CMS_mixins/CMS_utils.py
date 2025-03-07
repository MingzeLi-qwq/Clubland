import os
import uuid
from datetime import datetime

def upload_img_func(instance, filename):
    """
    上传附件时生成文件保存路径，示例格式：attachments/2025/02/18/随机UUID.扩展名
    """
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    today = datetime.today().strftime('%Y/%m/%d')
    return os.path.join("attachments", today, new_filename)

# 新增 UserFormMixin 封装表单常用方法
class UserFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
