from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from user_system.forms import LoginForm, SignUpForm
from user_system.helpers.mixins import UserTypeRequiredMixin
from club_system.helpers.mixins import ClubMemberRequiredMixin, ClubExistsRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from club_system.models import Membership, NewClubRequest, Club
from event_system.models import Event
from news_system.models import News
from news_system.views import get_first_image_url, enhance_news_with_image
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth import get_user_model
from news_system.models import News
import re
from django.utils.html import strip_tags



def home(request):
    """Display the application's start/home screen."""
    if request.user.is_authenticated:
        return redirect('Mine')  # Redirect authenticated users to Mine page
    
    page = request.GET.get('page', 1)
    events_per_page = 3
    
    upcoming_events_list = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')
    
    # Query the latest communities - sort by creation time in reverse order, and select the most recent 3
    new_clubs = Club.objects.order_by('-club_id')[:3]
    
    # Query the latest news - sort in reverse order of creation time, and take the latest 3
    news_items = News.objects.order_by('-created_at')[:3]
    
    # Use functions in the news_system to enhance news data
    enhanced_news = [enhance_news_with_image(news) for news in news_items]
    
    paginator = Paginator(upcoming_events_list, events_per_page)
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)
    
    # Handling AJAX Requests
    if request.GET.get('ajax'):
        # Rendering a partial template
        events_html = render_to_string('shared/events_list.html', {'events': events})
        pagination_html = render_to_string('shared/pagination.html', {'events': events})
        
        return JsonResponse({
            'events_html': events_html,
            'pagination_html': pagination_html,
            'current_page': events.number,
            'total_pages': paginator.num_pages,
            'has_next': events.has_next(),
            'has_previous': events.has_previous(),
        })
    
    return render(request, 'shared/home.html', {
        'events': events,
        'new_clubs': new_clubs,
        'recent_news': enhanced_news,
    })





class SignUpView(View):
    template_name = "user_system/sign_up.html"

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        else:
            return render(request, self.template_name, {"form": form})

class LogInView(View):
    template_name = "user_system/log_in.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = AuthenticationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"form": form})

def LogOutView(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    # Redirect directly to the login page, not the home page!
    return redirect('login')


# def societies(request):
#     """Societies List View"""
#     return render(request, 'shared/societies.html')

def events(request):
    """Events List View"""
    return render(request, 'shared/events.html')
    

"""This method is used to handle password change requests from User Dashboard"""
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Preventing users from being logged out
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard_personal_information') # Redirect to profile page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'user_system/dashboard/personal_information.html', {'form': form})


"""The following content is responsible for rendering the Personal Dashboard"""
class DashboardPersonalInformation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_system/dashboard/personal_information.html')

class DashboardMyClub(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, *args, **kwargs):
        user = request.user
        # Get the communities that the user is an administrator of
        managed_clubs = Membership.objects.filter(user=user, is_manager=True)
        # Get the communities of which the user is a regular member
        member_clubs = Membership.objects.filter(user=user, is_manager=False)
        
        return render(request, 'user_system/dashboard/my_club.html', {
            'managed_clubs': managed_clubs,
            'member_clubs': member_clubs
    })

class DashboardMyRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, *args, **kwargs):
        return render(request, 'user_system/dashboard/requests/my_requests.html')


"""The following content is used to process the request to view New Club Requests in Personal Dashboard"""
class NewClubRequestsView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request):
        pending_requests = NewClubRequest.objects.filter(creator=request.user, status=NewClubRequest.STATUS_PENDING)
        approved_requests = NewClubRequest.objects.filter(creator=request.user, status=NewClubRequest.STATUS_APPROVED)
        rejected_requests = NewClubRequest.objects.filter(creator=request.user, status=NewClubRequest.STATUS_REJECTED)

        context = {
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
        }
        return render(request, 'user_system/dashboard/requests/new_club_requests.html', context)
    
"""The following content is used to render the request to view the club membership detail in the personal dashboard"""
class ClubMembershipDetail(LoginRequiredMixin, ClubExistsRequiredMixin, UserTypeRequiredMixin, ClubMemberRequiredMixin, View):
    allowed_types = ['User']
    
    def get(self, request, club_id):
        try:
            # Try to get the current user's membership in the specified club
            membership = Membership.objects.get(user=request.user, club_id=club_id)
        except Membership.DoesNotExist:
            # If membership does not exist, add error message and redirect
            messages.error(request, "The specified membership does not exist.")
            return redirect('dashboard_my_club')

        # If the membership exists, render the details page
        context = {
            'membership': membership
        }
        return render(request, 'user_system/dashboard/my_club_detail.html', context)

@login_required
def Mine(request):
    """Mine view"""
    # Check if user is an admin
    if hasattr(request.user, 'account_type') and request.user.account_type == 'Admin':
        # Admin view - get all data for dashboard
        all_clubs = Club.objects.all()
        all_events = Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')
        
        # Get user count - import User model at the top of the file
        User = get_user_model()
        users_count = User.objects.count()
        
        # Get news count - import News model at the top of the file
        news_count = News.objects.count()
        
        return render(request, 'user_system/mine.html', {
            'clubs': all_clubs,
            'events': all_events,
            'users_count': users_count,
            'news_count': news_count,
        })
    else:
        # Regular user view - original functionality
        user_clubs = Club.objects.filter(membership__user=request.user)
        
        # Get user's upcoming events (both club events and RSVPed events)
        upcoming_events = Event.objects.filter(
            Q(club__in=user_clubs) |  # Events from user's clubs
            Q(rsvp__user=request.user),  # Events user has RSVPed to
            start_time__gte=timezone.now()
        ).distinct().order_by('start_time')
        
        new_clubs = Club.objects.order_by('-club_id')[:3]
        news_items = News.objects.order_by('-created_at')[:3]
        enhanced_news = [enhance_news_with_image(n) for n in news_items]
        
        return render(request, 'user_system/mine.html', {
            'clubs': user_clubs,
            'events': upcoming_events,
            'new_clubs': new_clubs,
            'recent_news': enhanced_news,
        })

def about_us(request):
    """about_us Page"""
    return render(request, 'shared/about_us.html')

# CSRF failure handling view
def csrf_failure(request, reason=""):
    """
    Custom CSRF error handling view to improve user experience
    - For AJAX requests, return JSON error
    - For normal requests, display a popup window and redirect back to the previous page
    """
    error_message = "You may have switched between different accounts too quickly.\nPlease wait a short moment and try again. (CSRF validation)"
    
    # Determine whether it is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': error_message
        }, status=403)
    
    # For normal requests, return a response with a popup window and a script to return to the previous page
    response = HttpResponse("""
    <html>
    <head><title>Account Security Verification Notice</title></head>
    <body>
        <script>
            alert("{}");
            history.back();
        </script>
    </body>
    </html>
    """.format(error_message))
    
    response.status_code = 403
    return response




