from django import forms
from django_summernote.widgets import SummernoteWidget
from club_system.models import Club
from event_system.models import Event
from .models import News, Comment
from CMS_mixins.CMS_utils import set_club_field, set_event_field

# 要求：
# 普通用户只能选择他们管理（is_manager）的社团
# 管理员可以选择全部的社团，并允许社团为空
# 根据所选社团过滤所属活动，并在验证时确保若已选择活动，其所属社团与所选社团一致（如果社团为空则不允许选择活动）。

class NewsForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        min_length=1,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100'  # 修改：使用 w-100 让输入框占满整行
        })
    )
    # 修改: 将字段名称从 category 改为 club，显示名称保持不变
    club = forms.ModelChoiceField(
        queryset=Club.objects.none(), 
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width:600px;'
        })
    )
    # 根据所选社团过滤所属活动
    event = forms.ModelChoiceField(
        queryset=Event.objects.none(), 
        required=False, 
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width:600px;'
        })
    )
    content = forms.CharField(widget=SummernoteWidget(attrs={'placeholder': '请输入正文...'}))
    
    class Meta:
        model = News
        # 修改: 调整字段顺序
        fields = ['title', 'club', 'event', 'content']
        labels = {
            'title': '标题',
            'club': '所属社团',
            'event': '所属活动',
            'content': '正文',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(NewsForm, self).__init__(*args, **kwargs)
        set_club_field(self, user, manage_only=True)
        set_event_field(self, self.data, self.instance, 'club', 'event')

    def clean(self):
        cleaned_data = super().clean()
        club = cleaned_data.get('club')
        event = cleaned_data.get('event')
        # 修改: 未选择社团则不允许选择活动
        if not club and event:
            self.add_error('event', forms.ValidationError("未选择社团时，不允许选择活动"))
        # 如果同时选择了社团和活动，校验活动所属社团是否与所选一致
        if club and event and event.club != club:
            self.add_error('event', forms.ValidationError("选择的活动不属于所选的社团"))
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
