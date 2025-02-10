from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import BlogPost
from .forms import BlogPostForm

# 博客列表页：显示所有博客文章
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blogpost_list.html'  # 模板文件名称
    context_object_name = 'posts'         # 在模板中通过 'posts' 变量访问查询结果
    paginate_by = 10                      # 可选：每页显示 10 篇

    def get_queryset(self):
        order = self.request.GET.get('order', 'desc')
        if order == 'asc':
            return BlogPost.objects.all().order_by('created_at')
        return BlogPost.objects.all().order_by('-created_at')

# 博客详情页：显示单篇博客文章的内容
class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blogpost_detail.html'
    context_object_name = 'post'

# 博客创建页：提供一个表单供用户创建新的博客文章
class BlogPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogpost_form.html'
    success_url = reverse_lazy('forum_system:blog_list')  # 提交成功后重定向到列表页
