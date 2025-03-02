from django import forms
from django_summernote.widgets import SummernoteWidget
from club_system.models import Club
from .models import BlogPost, Comment

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        min_length=1,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100'  # 修改：使用 w-100 让输入框占满整行
        })
    )
    # 修改: 将字段名称从 category 改为 club，显示名称保持不变
    category = forms.ModelChoiceField(
        queryset=Club.objects.none(), 
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width:600px;'
        })
    )
    content = forms.CharField(widget=SummernoteWidget(attrs={'placeholder': '请输入正文...'}))


    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'content']
        labels = {
            'title': '标题',
            'content': '正文',
            'category': '所属社团',
        }

    def __init__(self, *args, **kwargs):
        # 从视图中传入 user 参数
        user = kwargs.pop("user", None)
        super(BlogPostForm, self).__init__(*args, **kwargs)
        if user:
            if user.is_admin:
                # 管理员可选所有社团
                self.fields['category'].queryset = Club.objects.all()
            else:
                # 普通用户只显示已加入的社团
                self.fields['category'].queryset = user.clubs_joined.all()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': '评论内容',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入评论内容...'
            }),
        }
