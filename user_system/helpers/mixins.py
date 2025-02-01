from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.http import HttpResponse


class LoginRequiredMixin(AccessMixin):
    """限制视图只能被已登录用户访问"""
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

from django.http import HttpResponse
from django.utils.safestring import mark_safe

class UserTypeRequiredMixin(AccessMixin):
    """只允许特定用户类型访问，例如 'User' 或 'Admin', 在allowed_types中设置"""
    allowed_types = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.account_type not in self.allowed_types:
            message = """
            <html>
            <head>
                <meta charset="UTF-8">
                <script>
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 3000);  // 3秒后跳转
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ 你没有权限访问此页面</h2>
                <p style="text-align:center;">即将跳转到首页...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)

