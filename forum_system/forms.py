from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(max_length=200, min_length=1)
    content = forms.CharField(widget=CKEditorUploadingWidget(attrs={'placeholder': '请输入正文...'}))

    class Meta:
        model = BlogPost
        fields = ['title', 'content']  # removed 'author' and 'category'
        labels = {
            'title': '标题',
            'content': '正文',
        }
