from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.core.files.storage import default_storage
from .models import BlogPost, ThreadPost
from .forms import BlogPostForm, ThreadPostForm
from CMS_mixins.CMS_utils import UserFormMixin, get_paginate_by_request  # 修改：导入通用函数
from club_system.models import Club

# 博客列表页：显示所有博客文章
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blogpost_list.html'  # 模板文件名称
    context_object_name = 'posts'         # 在模板中通过 'posts' 变量访问查询结果

    def get_queryset(self):
        queryset = super().get_queryset()
        club_filter = self.request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club_id=club_filter)
        order = self.request.GET.get('order', 'desc')
        if order == 'asc':
            return queryset.order_by('created_at')
        return queryset.order_by('-created_at')
    
    def get_paginate_by(self, queryset):
        return get_paginate_by_request(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = Club.objects.all()
        return context


# 博客详情页：显示单篇博客文章的内容
class BlogPostDetailView(FormMixin, DetailView):
    model = BlogPost
    template_name = 'blogpost_detail.html'
    context_object_name = 'post'
    form_class = ThreadPostForm

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = self.get_form()
        # 新增讨论的排序和分页
        from django.core.paginator import Paginator
        threadposts_qs = self.object.thread_posts.all()
        order_thread = self.request.GET.get('order_thread', 'desc')
        if order_thread == 'asc':
            threadposts_qs = threadposts_qs.order_by('created_at')
        else:
            threadposts_qs = threadposts_qs.order_by('-created_at')
        per_page_thread = self.request.GET.get('per_page_thread', 5)
        try:
            per_page_thread = int(per_page_thread)
        except ValueError:
            per_page_thread = 5
        paginator = Paginator(threadposts_qs, per_page_thread)
        page_number = self.request.GET.get('page_thread')
        page_obj_thread = paginator.get_page(page_number)
        context['threadposts'] = page_obj_thread.object_list
        context['page_obj_thread'] = page_obj_thread
        context['paginator_thread'] = paginator
        context['order_thread'] = order_thread
        context['per_page_thread'] = per_page_thread
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread_post = form.save(commit=False)
        thread_post.author = self.request.user
        thread_post.blog_post = self.object
        thread_post.save()
        return HttpResponseRedirect(self.get_success_url())

# 博客创建页：提供一个表单供用户创建新的博客文章
class BlogPostCreateView(LoginRequiredMixin, UserFormMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogpost_form.html'
    success_url = reverse_lazy('forum_system:blog_list')  # 提交成功后重定向到列表页

    # ...existing代码已被抽象到 UserFormMixin 中...
    


class ThreadPostCreateView(LoginRequiredMixin, CreateView):
    model = ThreadPost
    form_class = ThreadPostForm
    template_name = 'comment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        # 假设评论关联的 BlogPost 是通过 URL 参数传递的 blog_post_id
        form.instance.blog_post_id = self.kwargs.get('blog_post_id')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('forum_system:blog_detail', kwargs={'pk': self.kwargs.get('blog_post_id')})


class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    template_name = 'blogpost_confirm_delete.html'
    success_url = reverse_lazy('forum_system:blog_list')

    def test_func(self):
        return self.request.user == self.get_object().author

class ThreadPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ThreadPost
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        return reverse('forum_system:blog_detail', kwargs={'pk': self.get_object().blog_post.pk})

    def test_func(self):
        return self.request.user == self.get_object().author



