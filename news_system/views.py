from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, JsonResponse
from .models import News, Comment
from .forms import NewsForm, CommentForm
from event_system.models import Event
from club_system.models import Club  # 新增导入以获取所有社团
from CMS_mixins.CMS_utils import UserFormMixin, get_paginate_by_request  # 修改：导入通用函数
from CMS_mixins.CMS_utils import RTEUploadUtils  # 新增导入
from django.db.models import Q

# 新闻列表页：显示所有新闻文章
class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'  # 模板文件名称
    context_object_name = 'posts'         # 在模板中通过 'posts' 变量访问查询结果

    def get_queryset(self):
        queryset = News.objects.all()
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
        club_filter = self.request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club__pk=club_filter)
        # 默认以时间倒序排列新闻；当 GET 参数 order 缺省或不为 'asc' 时，按降序排序
        order = self.request.GET.get('order', 'desc')
        if order == 'asc':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')
        return queryset
    
    def get_paginate_by(self, queryset):
        return get_paginate_by_request(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = Club.objects.all()  # 增加 clubs 上下文变量
        return context


# 新闻详情页：显示单篇新闻文章的内容
class NewsDetailView(FormMixin, DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'post'
    form_class = CommentForm

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the comment form only if user is authenticated
        if self.request.user.is_authenticated:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.news = self.object
        comment.save()
        return HttpResponseRedirect(self.get_success_url())

# 新闻创建页：提供一个表单供用户创建新的新闻文章
class NewsCreateView(LoginRequiredMixin, UserFormMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'news_form.html'
    success_url = reverse_lazy('news_system:news_list')  # 提交成功后重定向到列表页


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        # 假设评论关联的 News 是通过 URL 参数传递的 news_id
        form.instance.news_id = self.kwargs.get('news_id')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('news_system:news_detail', kwargs={'pk': self.kwargs.get('news_id')})


class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    template_name = 'news_confirm_delete.html'
    success_url = reverse_lazy('news_system:news_list')

    def test_func(self):
        return self.request.user == self.get_object().author

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        RTEUploadUtils.delete_associated_images(instance)
        return super().delete(request, *args, **kwargs)

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        return reverse('news_system:news_detail', kwargs={'pk': self.get_object().news.pk})

    def test_func(self):
        return self.request.user == self.get_object().author

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        RTEUploadUtils.delete_associated_images(instance)
        return super().delete(request, *args, **kwargs)

def load_events(request):
    club_id = request.GET.get('club')
    events = Event.objects.filter(club_id=club_id).order_by('name')
    # 返回活动的 id 和名称
    events_data = list(events.values('id', 'name'))
    return JsonResponse(events_data, safe=False)



