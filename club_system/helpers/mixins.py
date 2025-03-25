from django.contrib.auth.mixins import AccessMixin
# from django.shortcuts import redirect
from django.http import HttpResponse
from club_system.models import Club, Membership
from user_system.models import User
from django.utils.safestring import mark_safe

class ClubMemberRequiredMixin(AccessMixin):
    """Access is limited to club members only"""
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
                    }, 3000);  // Jump in 3 seconds / Jump in 3 seconds
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You are not a member of this club and cannot access this page</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            # Add 403 status code
            return HttpResponse(mark_safe(message), status=403)
        return super().dispatch(request, *args, **kwargs)

class ClubManagerRequiredMixin(AccessMixin):
    """Only allow access to club managers"""
    def dispatch(self, request, *args, **kwargs):
        club_id = kwargs.get('club_id')
        """Give @superuser permission to override club manager checks (recommended to remove before going live)"""
        if request.user.username == "@superuser":
            return super().dispatch(request, *args, **kwargs)
        
        """Give admin permission to override club manager checks (recommended to remove before going live)"""
        if request.user.account_type == 'Admin':
            return super().dispatch(request, *args, **kwargs)
        

        if not Membership.objects.filter(user=request.user, club_id=club_id, is_manager=True).exists():
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
                <h2 style="text-align:center; margin-top:20%;">❌ You are not an administrator of this organization and cannot access this page.</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            # Add 403 status code
            return HttpResponse(mark_safe(message), status=403) 
        return super().dispatch(request, *args, **kwargs)
    
class NonClubManagerRequiredMixin(AccessMixin):
    """Blocking access by association manager"""
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
                    }, 3000);  // Jump in 3 seconds
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You are the club manager and cannot access this page.</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            # Add 403 status code
            return HttpResponse(mark_safe(message), status=403)
        return super().dispatch(request, *args, **kwargs)

class NonClubMemberRequiredMixin(AccessMixin):
    """Access is only allowed to non-members of the association"""
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
                    }, 3000);  // Jump in 3 seconds / Jump in 3 seconds
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ You are already a member of the society and cannot access this page</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            # Add 403 status code
            return HttpResponse(mark_safe(message), status=403)
        return super().dispatch(request, *args, **kwargs)
    
class ClubExistsRequiredMixin(AccessMixin):
    """Check if club exists"""
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
                    }, 3000);  // Jump in 3 seconds
                </script>
            </head>
            <body>
                <h2 style="text-align:center; margin-top:20%;">❌ The club does not exist</h2>
                <p style="text-align:center;">Coming soon to the home page...</p>
            </body>
            </html>
            """
            return HttpResponse(mark_safe(message), status=404)
        return super().dispatch(request, *args, **kwargs)