from django.contrib.auth.mixins import AccessMixin
# from django.shortcuts import redirect
from django.http import HttpResponse
from club_system.models import Club, Membership
from django.utils.safestring import mark_safe

class ClubMemberRequiredMixin(AccessMixin):
    """Access is limited to club members only"""
    """只允许社团成员访问"""
    def dispatch(self, request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        if not Membership.objects.filter(user=request.user, club_id=club_id).exists():
            message = """
            <html>
            <head>
                <meta charset="UTF-8">
                <script>
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 3000);  // Jump in 3 seconds / 3秒后跳转
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You are not a member of this club and cannot access this page</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)

class ClubManagerRequiredMixin(AccessMixin):
    """Only allow access to club managers"""
    """只允许社团管理员访问"""
    def dispatch(self, request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        if not Membership.objects.filter(user=request.user, club_id=club_id, is_manager=True).exists():
            message = """
            <html>
            <head>
                <meta charset="UTF-8">
                <script>
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 3000);  // Jump in 3 seconds / 3秒后跳转
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You are not an administrator of this organization and cannot access this page.</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)
    
class NonClubManagerRequiredMixin(AccessMixin):
    """阻止社团管理员访问"""
    def dispatch(self, request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        if Membership.objects.filter(user=request.user, club_id=club_id, is_manager=True).exists():
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
                <h2 style="text-align:center; margin-top:20%;">❌ You are the club administrator and cannot access this page.</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)

class NonClubMemberRequiredMixin(AccessMixin):
    """Access is only allowed to non-members of the association"""
    """只允许非社团成员访问"""
    def dispatch(self, request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        if Membership.objects.filter(user=request.user, club_id=club_id).exists():
            message = """
            <html>
            <head>
                <meta charset="UTF-8">
                <script>
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 3000);  // Jump in 3 seconds / 3秒后跳转
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You are already a member of the society and cannot access this page</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)
    
class ClubExistsRequiredMixin(AccessMixin):
    """检查 club 是否存在"""
    def dispatch(self, request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        if not Club.objects.filter(pk=club_id).exists():
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
                <h2 style="text-align:center; margin-top:20%;">❌ The club does not exist</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message))  # mark_safe 让 HTML 代码生效
        return super().dispatch(request, *args, **kwargs)