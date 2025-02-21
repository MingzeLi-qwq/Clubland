import os
import uuid
from datetime import datetime

def upload_img_func(instance, filename):
    """
    上传附件时生成文件保存路径，示例格式：attachments/2025/02/18/随机UUID.扩展名
    """
    # print("上传附件函数被调用")
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    today = datetime.today().strftime('%Y/%m/%d')
    return os.path.join("attachments", today, new_filename)