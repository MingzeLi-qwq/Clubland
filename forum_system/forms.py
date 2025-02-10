from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 修改此行
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(attrs={'placeholder': '请输入正文...'}))

    class Meta:
        model = BlogPost
        fields = '__all__'
        labels = {
            'title': '标题',
            'content': '正文',
        }
