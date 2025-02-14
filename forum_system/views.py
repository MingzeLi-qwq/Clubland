from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from .models import BlogPost, Comment
from .forms import BlogPostForm, CommentForm

# 博客列表页：显示所有博客文章
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blogpost_list.html'  # 模板文件名称
    context_object_name = 'posts'         # 在模板中通过 'posts' 变量访问查询结果

    def get_queryset(self):
        order = self.request.GET.get('order', 'desc')
        if order == 'asc':
            return BlogPost.objects.all().order_by('created_at')
        return BlogPost.objects.all().order_by('-created_at')
    
    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if per_page and per_page.isdigit():
            return int(per_page)
        return 10  # 默认每页 10 个


# 博客详情页：显示单篇博客文章的内容
class BlogPostDetailView(FormMixin, DetailView):
    model = BlogPost
    template_name = 'blogpost_detail.html'
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
        comment.blog_post = self.object
        comment.save()
        return HttpResponseRedirect(self.get_success_url())

# 博客创建页：提供一个表单供用户创建新的博客文章
class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogpost_form.html'
    success_url = reverse_lazy('forum_system:blog_list')  # 提交成功后重定向到列表页


    def form_valid(self, form):
        # 自动将当前登录用户赋值给作者字段
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def sceneImgUpload(request):
        if request.method == 'POST':
            callback = request.GET.get('CKEditorFuncNum')
            try:
                path = "static/upload/" + time.strftime("%Y%m%d%H%M%S", time.localtime())
                f = request.FILES["upload"]
                file_name = path + "_" + f.name
                des_origin_f = open(file_name, "wb+")
                for chunk in f.chunks():
                    des_origin_f.write(chunk)
                des_origin_f.close()
            except Exception as e:
                print(e)
            res = "<script>window.parent.CKEDITOR.tools.callFunction(" + callback + ",'/" + file_name + "', '');</script>"
            return HttpResponse(res)
        else:
            raise Http404()


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
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

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        return reverse('forum_system:blog_detail', kwargs={'pk': self.get_object().blog_post.pk})

    def test_func(self):
        return self.request.user == self.get_object().author

@csrf_exempt  # 如果需要，可暂时关闭 CSRF 检查，确保上传正常
def ckeditor_image_upload(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        image = request.FILES['upload']
        # 保存文件到默认存储目录下，建议在 production 中配置合适的 MEDIA_ROOT
        file_path = default_storage.save('uploads/' + image.name, image)
        file_url = default_storage.url(file_path)

        return JsonResponse({
            "uploaded": 1,
            "fileName": image.name,
            "url": file_url,
        })
    else:
        return JsonResponse({
            "uploaded": 0,
            "error": {"message": "没有上传文件"}
        })


