from django import forms
from django_summernote.widgets import SummernoteWidget
from club_system.models import Club
from event_system.models import Event
from .models import BlogPost, Comment

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(max_length=200, min_length=1)
    # 先选择所属社团
    category = forms.ModelChoiceField(queryset=Club.objects.none(), label="所属社团")
    # 根据所选社团过滤所属活动，此处默认空
    event = forms.ModelChoiceField(queryset=Event.objects.none(), required=False, label="所属活动")
    content = forms.CharField(widget=SummernoteWidget(attrs={'placeholder': '请输入正文...'}))

    class Meta:
        model = BlogPost
        # 调整字段顺序: 先社团再活动
        fields = ['title', 'category', 'event', 'content']
        labels = {
            'title': '标题',
            'category': '所属社团',
            'event': '所属活动',
            'content': '正文',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(BlogPostForm, self).__init__(*args, **kwargs)
        if user:
            if user.is_admin:
                self.fields['category'].queryset = Club.objects.all()
            else:
                self.fields['category'].queryset = user.clubs_joined.all()
        # 设置活动选择列表：如果表单提交数据中有 category，则根据其过滤活动
        if self.data.get('category'):
            try:
                club_id = int(self.data.get('category'))
                self.fields['event'].queryset = Event.objects.filter(club_id=club_id)
            except (ValueError, TypeError):
                self.fields['event'].queryset = Event.objects.none()
        elif self.instance.pk and self.instance.category:
            self.fields['event'].queryset = Event.objects.filter(club=self.instance.category)
        else:
            self.fields['event'].queryset = Event.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        event = cleaned_data.get('event')
        # 如果同时选择了社团和活动，校验活动所属社团是否与所选一致
        if event and category and event.club != category:
            raise forms.ValidationError("选择的活动不属于所选的社团")
        return cleaned_data

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
