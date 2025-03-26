from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, JsonResponse
from .models import News, Comment
from .forms import NewsForm, CommentForm
from event_system.models import Event
from club_system.models import Club
from CMS_mixins.CMS_utils import UserFormMixin, get_paginate_by_request
from CMS_mixins.CMS_utils import RTEUploadUtils
from django.db.models import Q
from bs4 import BeautifulSoup

def get_first_image_url(content):
    """从内容中提取第一张图片的URL
    
    Args:
        content (str): HTML格式的内容
        
    Returns:
        str: 图片URL或None
    """
    first_image_url = None
    if content:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(content, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and img_tag.has_attr('src'):
            first_image_url = img_tag['src']
    return first_image_url

def enhance_news_with_image(news_item):
    """增强新闻数据，添加图片URL
    
    Args:
        news_item (News): 新闻对象
        
    Returns:
        dict: 增强后的新闻数据
    """
    return {
        'id': news_item.id,
        'title': news_item.title,
        'author': news_item.author,
        'club': news_item.club,
        'event': news_item.event,
        'first_image_url': get_first_image_url(news_item.content),
        'created_at': news_item.created_at,
        'url': f'/news/{news_item.id}/'
    }

# 新闻列表页：显示所有新闻文章
class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = News.objects.all()
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
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
        return get_paginate_by_request(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = Club.objects.all()
        
        # 每个新闻的first_image_url属性
        for post in context['posts']:
            post.first_image_url = get_first_image_url(post.content)
            
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
        # 移除可能由父类FormMixin添加的表单
        if 'form' in context:
            del context['form']
        # 只有登录用户才会获得评论表单
        if self.request.user.is_authenticated:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        # 如果用户未登录，直接返回未授权错误或重定向到登录页
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
            
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
    
    def form_valid(self, form):
        # 确保正确保存作者信息
        form.instance.author = self.request.user
        # print("表单验证成功，准备保存...")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # print(f"表单验证失败: {form.errors}")
        return super().form_invalid(form)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user

        form.instance.news_id = self.kwargs.get('news_id')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('news_system:news_detail', kwargs={'pk': self.kwargs.get('news_id')})


class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    success_url = reverse_lazy('news_system:news_list')

    def test_func(self):
        # 允许作者或管理员删除
        return self.request.user == self.get_object().author or self.request.user.is_admin

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        RTEUploadUtils.delete_associated_images(self.object)
        success_url = self.get_success_url()
        self.object.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return HttpResponseRedirect(success_url)
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.delete(request, *args, **kwargs)
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_success_url())

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        # 需要确保先设置 self.object
        if not hasattr(self, 'object') or not self.object:
            self.object = self.get_object()
        return reverse('news_system:news_detail', kwargs={'pk': self.object.news.pk})

    def test_func(self):
        # 允许作者或管理员删除
        return self.request.user == self.get_object().author or self.request.user.is_admin

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        RTEUploadUtils.delete_associated_images(self.object)
        success_url = self.get_success_url()
        self.object.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return HttpResponseRedirect(success_url)
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.delete(request, *args, **kwargs)
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # 如果是直接访问删除URL，重定向到新闻详情页
        return HttpResponseRedirect(self.get_success_url())

def load_events(request):
    club_id = request.GET.get('club')
    events = Event.objects.filter(club_id=club_id).order_by('name')
    # 返回活动的 id 和名称
    events_data = list(events.values('id', 'name'))
    return JsonResponse(events_data, safe=False)



