from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.http import HttpResponse


class LoginRequiredMixin(AccessMixin):
    """Restrict view access to logged-in users only"""
    """限制视图只能被已登录用户访问"""
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

from django.http import HttpResponse
from django.utils.safestring import mark_safe

class UserTypeRequiredMixin(AccessMixin):
    """Access is only allowed for certain User types, such as 'User' or 'Admin', set in allowed_types"""
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
                    }, 3000);  // Jump in 3 seconds / Jump in 3 seconds
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You do not have permission to access this page</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)

