from django import forms
from django_summernote.widgets import SummernoteWidget
from club_system.models import Club
from event_system.models import Event
from .models import BlogPost, Comment

# 要求：
# 普通用户只能选择他们管理（is_manager）的社团
# 管理员可以选择全部的社团，并允许社团为空
# 根据所选社团过滤所属活动，并在验证时确保若已选择活动，其所属社团与所选社团一致（如果社团为空则不允许选择活动）。

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        min_length=1,
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # 使用 form-control 样式
            'style': 'width:600px;'
        })
    )
    # 先选择所属社团
    category = forms.ModelChoiceField(
        queryset=Club.objects.none(), 
        label="所属社团",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width:600px;'
        })
    )
    # 根据所选社团过滤所属活动
    event = forms.ModelChoiceField(
        queryset=Event.objects.none(), 
        required=False, 
        label="所属活动",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width:600px;'
        })
    )
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
                # 管理员可以选择全部社团，并允许置空
                self.fields['category'].queryset = Club.objects.all()
                self.fields['category'].required = False
            else:
                # 普通用户只能选择其管理的社团
                self.fields['category'].queryset = Club.objects.filter(
                    membership__user=user, membership__is_manager=True
                ).distinct()
        # 根据已提交数据中的社团自动过滤该社团下的活动
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
        # 如果未选择社团，则不允许选择活动
        if not category and event:
            raise forms.ValidationError("未选择社团时，不允许选择活动")
        # 如果同时选择了社团和活动，校验活动所属社团是否与所选一致
        if category and event and event.club != category:
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
