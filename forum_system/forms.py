from django import forms
from django_summernote.widgets import SummernoteWidget
from club_system.models import Club
from .models import BlogPost, Comment

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        min_length=1,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100'
        })
    )
    # 将字段名称从 category 改为 club
    club = forms.ModelChoiceField(
        queryset=Club.objects.none(), 
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width:600px;'
        })
    )
    content = forms.CharField(widget=SummernoteWidget(attrs={'placeholder': '请输入正文...'}))

    class Meta:
        model = BlogPost
        fields = ['title', 'club', 'content']
        labels = {
            'title': '标题',
            'content': '正文',
            'club': '所属社团',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(BlogPostForm, self).__init__(*args, **kwargs)
        if user:
            if user.is_admin:
                self.fields['club'].queryset = Club.objects.all()
            else:
                self.fields['club'].queryset = user.clubs_joined.all()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': '评论内容',
        }
        widgets = {
            'text': SummernoteWidget(attrs={'placeholder': '请输入评论内容...'}),
        }
