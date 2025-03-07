from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from .models import News, Comment
from .forms import NewsForm, CommentForm
from event_system.models import Event
from club_system.models import Club  # 新增导入以获取所有社团

# 新闻列表页：显示所有新闻文章
class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'  # 模板文件名称
    context_object_name = 'posts'         # 在模板中通过 'posts' 变量访问查询结果

    def get_queryset(self):
        queryset = News.objects.all()
        club_filter = self.request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club__pk=club_filter)
        order = self.request.GET.get('order', 'desc')
        if order == 'asc':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')
        return queryset
    
    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if (per_page and per_page.isdigit()):
            return int(per_page)
        return 10  # 默认每页 10 个

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
class NewsCreateView(LoginRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'news_form.html'
    success_url = reverse_lazy('news_system:news_list')  # 提交成功后重定向到列表页


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 添加当前用户到表单参数中
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # 自动将当前登录用户赋值给作者字段
        form.instance.author = self.request.user
        return super().form_valid(form)
    


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

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        return reverse('news_system:news_detail', kwargs={'pk': self.get_object().news.pk})


    def test_func(self):
        return self.request.user == self.get_object().author

def load_events(request):
    club_id = request.GET.get('club')
    events = Event.objects.filter(club_id=club_id).order_by('name')
    # 返回活动的 id 和名称
    events_data = list(events.values('id', 'name'))
    return JsonResponse(events_data, safe=False)



