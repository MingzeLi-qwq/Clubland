from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # 修改此行
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = BlogPost
        fields = '__all__'
