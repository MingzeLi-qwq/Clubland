from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.http import HttpResponse


class LoginRequiredMixin(AccessMixin):
    """Restrict view access to logged-in users only"""
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)

from django.http import HttpResponse
from django.utils.safestring import mark_safe

class UserTypeRequiredMixin(AccessMixin):
    """
    Access is only allowed for specific user types, such as 'User' or 'Admin',
    set in the 'allowed_types' list
    """
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
                    }, 3000);  // Redirect in 3 seconds
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You do not have permission to access this page</h2>
                <p style="text-align:center;">Redirecting to the home page shortly...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe allows HTML content to be rendered
        return super().dispatch(request, *args, **kwargs)