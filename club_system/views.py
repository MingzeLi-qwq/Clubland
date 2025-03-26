from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .models import Club, Membership, NewClubRequest
from user_system.models import User
from .helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, ClubManagerRequiredMixin
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from event_system.models import Event, RSVP, Category
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from club_system.helpers.mixins import ClubExistsRequiredMixin, ClubManagerRequiredMixin
from .forms import NewClubRequestForm
from django.utils import timezone
from notification_system.models import Notification

import urllib.parse
import json

"""------------------------------------------------------Checks if a string is a duplicate of an existing club name.---------------------------------------------------------"""
"""This method is used to render the Club list page"""
def clubs(request):
    search_query = request.GET.get('search', '')
    if search_query:
        clubs = Club.objects.filter(name__icontains=search_query)
    else:
        clubs = Club.objects.all()
    return render(request, 'clubs.html', {
        'clubs': clubs,
        'search_query': search_query
    })


"""This method checks for duplicate Club names, and more importantly, ignores case and spaces."""
def isSameClubNameExist(name):
    normalized_name = ''.join(name.split()).lower()
    clubs = Club.objects.all()
    for club in clubs:
        normalized_club_name = ''.join(club.name.split()).lower()
        if normalized_name == normalized_club_name:
            return True
    return False

"""This method checks for duplicate Club names on requirement, and more importantly, ignores case and spaces."""
def isSameClubNameExistInRequest(name):
    normalized_name = ''.join(name.split()).lower()
    requests = NewClubRequest.objects.all()
    for request in requests:
        normalized_request_name = ''.join(request.name.split()).lower()
        if normalized_name == normalized_request_name:
            return True
    return False

"""--------------------------------------------------------------------------------End-------------------------------------------------------------------------------"""


"""--------------------------------------------------------------------Club Details Page-------------------------------------------------------------------------------"""
"""This method is used to render the Club details page"""
class ClubDetailView(ClubExistsRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        events = Event.objects.filter(club=club)
        member_count = club.members.count()
        managers = club.membership_set.filter(is_manager=True)
        is_manager=False
        is_member=False
        
        recent_news = None
        if hasattr(club, 'news'):
            recent_news = club.news.all().order_by('-created_at')
            
            from bs4 import BeautifulSoup
            for news_item in recent_news:
                first_image_url = None
                if news_item.content:
                    soup = BeautifulSoup(news_item.content, 'html.parser')
                    img_tag = soup.find('img')
                    if img_tag and img_tag.has_attr('src'):
                        first_image_url = img_tag['src']
                news_item.first_image_url = first_image_url
            
        if request.user.is_authenticated:
            is_manager = managers.filter(user=request.user).exists()
            is_member = Membership.objects.filter(user=request.user, club=club).exists()       
        return render(request, 'club_detail.html', {
            'club': club,
            'member_count': member_count,
            'managers': managers,
            'is_manager': is_manager,
            'is_member': is_member,
            'events': events,
            'recent_news': recent_news,
        })
    
"""This method is used to handle member registration from user itself"""
class RegisterMembershipView(LoginRequiredMixin, ClubExistsRequiredMixin, UserTypeRequiredMixin, NonClubMemberRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        Membership.objects.get_or_create(user=request.user, club=club)
        return redirect('club_detail', club_id=club_id)

        
""""This method is used to handle membership cancelation from user it self"""
class CancelMembershipView(LoginRequiredMixin, ClubExistsRequiredMixin, UserTypeRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        Membership.objects.filter(user=request.user, club=club).delete()
        messages.success(request, f"You have successfully cancelled your membership in {club.name}.")
        return redirect('dashboard_my_club')
"""------------------------------------------------------------------------End-------------------------------------------------------------------------------"""
        

"""---------------------------------------------------Club Manager Side Bar------------------------------------------------------------"""
"""Those method is used to render the Club Manager Side Bar"""
class ClubManagerGeneral(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/general.html', {
            'club_id': club_id,
            'club': club,
        })
    
class ClubManagerMembers(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        
        # Get search parameters
        manager_search = request.GET.get('manager_search', '')
        member_search = request.GET.get('member_search', '')
        
        # Manager Enquiries
        managers = club.membership_set.filter(is_manager=True)
        if manager_search:
            managers = managers.filter(
                Q(user__first_name__icontains=manager_search) |
                Q(user__last_name__icontains=manager_search) |
                Q(user__email__icontains=manager_search)
            )
        
        # Members Enquiries
        muggles = club.membership_set.filter(is_manager=False)
        if member_search:
            muggles = muggles.filter(
                Q(user__first_name__icontains=member_search) |
                Q(user__last_name__icontains=member_search) |
                Q(user__email__icontains=member_search)
            )
        
        return render(request, 'club_manager/members.html', {
            'club_id': club_id,
            'club': club,
            'managers': managers,
            'muggles': muggles,
            'user': request.user,
            'manager_count': managers.count(),
            'muggle_count': muggles.count(),
            'manager_search_query': manager_search,
            'member_search_query': member_search,
        })
    
class ClubManagerNews(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/news.html', {
            'club_id': club_id,
            'club': club,
        })
    
class ClubManagerForum(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/forum.html', {
            'club_id': club_id,
            'club': club,
        })
    
class ClubManagerEvents(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, club_id=club_id)
        search_query = request.GET.get('search', '')
        events = Event.objects.filter(club=club)

        if search_query:
            events = events.filter(
                Q(name__icontains=search_query) |
                Q(start_time__icontains=search_query)
            )

        events = events.order_by('start_time')

        context = {
            'club': club,
            'events': events,
            'club_id': club_id,
            'search_query': search_query,
        }
        return render(request, 'club_manager/events.html', context)

class ClubManagerDashboard(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, club_id=club_id)

        return render(request, 'club_manager/dashboard.html', {
            'club_id': club_id,
            'club': club,
        })
        

"""------------------------------------------------------------End--------------------------------------------------------------"""



"""----------------------------------------------------------------Club Manager General-------------------------------------------------------------------"""
"""This method is used to handle name update requests from the club manager general and admin panel."""
class UpdateClubName(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        new_name = request.POST.get('club_name', '').strip()

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_general'
        else:
            redirect_url = 'club_manager_general'

        if new_name == club.name:
            messages.error(request, "The new name cannot duplicate the old name.")
            return redirect(redirect_url, club_id=club_id)

        if not new_name:
            messages.error(request, "Club name cannot be empty.")
            return redirect(redirect_url, club_id=club_id)
        
        if isSameClubNameExist(new_name):
            messages.error(request, "There's already a Club with the same name.")
            return redirect(redirect_url, club_id=club_id)
        
        if isSameClubNameExistInRequest(new_name):
            messages.error(request, "There's already a New Club Request with the same name.")
            return redirect(redirect_url, club_id=club_id)
            
        try:
            club.name = new_name
            club.save()
            messages.success(request, "Club name updated successfully.")
        except IntegrityError:
            messages.error(request, "This club name does not match the specification.")
        
        return redirect(redirect_url, club_id=club_id)

"""This method is used to handle description update requests from the club manager general and admin panel."""
class UpdateClubDescription(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        new_description = request.POST.get('club_description', '').strip()

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_general'
        else:
            redirect_url = 'club_manager_general'

        
        if new_description == club.description:
            messages.error(request, "The new description cannot duplicate the old description.")
            return redirect(redirect_url, club_id=club_id)

        if not new_description:
            new_description = "This Club hasn't added a Description yet"
            messages.success(request, "Empty content will use the default Description")
        
        club.description = new_description
        club.save()
        messages.success(request, "Description updated successfully.")
        
        return redirect(redirect_url, club_id=club_id)
"""------------------------------------------------------------------------End---------------------------------------------------------------------------"""


"""-------------------------------------------------------------Club Manager Members-------------------------------------------------------------------------"""
"""This section is used to process requests from club manager remove manager"""
class RemoveManagerView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        club = get_object_or_404(Club, pk=club_id)
        user = get_object_or_404(User, username=username)
        membership = get_object_or_404(Membership, club=club, user=user)

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'


        # Check if it is the last administrator
        if Membership.objects.filter(club=club, is_manager=True).count() <= 1:
            messages.error(request, "At least one manager is required.")
            return redirect(redirect_url, club_id=club_id)
        
        Notification.objects.create(
            user=membership.user,
            title="Manager Removed",
            message=f"You are no longer the manager of club {club.name}. Click 'continue' to check your membership",
            notification_type='general',
            url=reverse('dashboard_my_club_detail', args=[club_id]),
        )

        # Remove administrator status
        membership.is_manager = False
        membership.save()
        messages.success(request, f"{user.get_full_name} is no longer a manager.")
        return redirect(redirect_url, club_id=club_id)

"""This section is used to process requests from the club manager and admin panel to add a new manager."""
class SetManagerView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        club = get_object_or_404(Club, pk=club_id)
        user = get_object_or_404(User, username=username)
        membership = get_object_or_404(Membership, club=club, user=user)

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'

        Notification.objects.create(
            user=membership.user,
            title="Manager Membership",
            message=f"You are now the manager of club {club.name}. Click 'continue' to check your membership",
            notification_type='general',
            url=reverse('dashboard_my_club_detail', args=[club_id]),
        )

        # Set as manager
        membership.is_manager = True
        membership.save()
        messages.success(request, f"{user.get_full_name} is now a manager.")
        return redirect(redirect_url, club_id=club_id)

"""This section is used to implement the auto-search function of the club manager - Membership - Add members - auto-search box."""
class SearchUsersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        club_id = request.GET.get('club_id')
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            account_type=User.ACCOUNT_TYPE_USER
        ).exclude(membership__club_id=club_id)

        results = [{
            'username': user.username,
            'email': user.email,
            'full_name' : user.first_name + user.last_name,
        } for user in users]
        
        return JsonResponse(results, safe=False)
    
"""This section is used to implement the club manager's ability to remove Memberships."""
class RemoveMemberView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username, *args, **kwargs):
        club = get_object_or_404(Club, club_id=club_id)
        user_to_remove = User.objects.filter(username=username).first()

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'
        
        # Check if the user exists
        if not user_to_remove:
            messages.error(request, "User not exists")
            return redirect(redirect_url, club_id=club_id)

        membership = Membership.objects.filter(user=user_to_remove, club=club).first()
        # Check if you have this membership relationship
        if not membership:
            messages.error(request, "The user does not belong to this club")
            return redirect(redirect_url, club_id=club_id)
        
        # Check if you are an administrator
        if membership.is_manager:
            messages.error(request, "The user is an administrator and cannot be removed directly")
            return redirect(redirect_url, club_id=club_id)
        
        Notification.objects.create(
            user=membership.user,
            title="Remove Membership",
            message=f"You have been removed from {club.name}.",
            notification_type='general',
        )

        membership.delete()
        messages.success(request, f"{user_to_remove.username} has been removed from the club.")
        return redirect(redirect_url, club_id=club_id)

"""This section is used to implement the club manager - add member functionality."""
class AddMemberView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'

        try:
            club = Club.objects.get(club_id=club_id)
            user = User.objects.get(username=username)
            
            if Membership.objects.filter(user=user, club=club).exists():
                messages.error(request, f"{user.username} Already a member of this Club")
                return redirect(redirect_url, club_id=club_id)
                
            Membership.objects.create(user=user, club=club)

            Notification.objects.create(
                user=user,
                title="New Membership",
                message=f"You have been added as a member in {club.name}.",
                notification_type='general',
            )

            messages.success(request, f"Successfully added member {user.get_full_name()}")
            return redirect(redirect_url, club_id=club_id)
            
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect(redirect_url, club_id=club_id)
            
        except Exception as e:
            messages.error(request, f"Add failed: {str(e)}")
            return redirect(redirect_url, club_id=club_id)
          
"""----------------------------------------------------------------------End--------------------------------------------------------------"""



    
"""-------------------------------------------------------Club Manager Event Related-------------------------------------------------------"""
    
class ClubManagerEventGeneral(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, event_id, *args, **kwargs ):
        club = get_object_or_404(Club, club_id=club_id)
        event = get_object_or_404(Event, pk=event_id)
        all_categories = Category.objects.all()
        context = {
            'club': club,
            'event': event,
            'club_id': club_id,
            'all_categories': all_categories,
        }
        return render(request, 'club_manager/event/general.html', context)
    
class ClubManagerEventRSVPs(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, event_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, pk=event_id)
        
        search_query = request.GET.get('search', '')
        rsvps = RSVP.objects.filter(event=event).select_related('user')
        
        if search_query:
            rsvps = rsvps.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        context = {
            'club': club,
            'event': event,
            'club_id': club_id,
            'rsvps': rsvps,
            'search_query': search_query,
        }
        return render(request, 'club_manager/event/RSVPs.html', context)
    
"""-------------------------------------------------------Club Manager Event Related end-------------------------------------------------------"""




"""-------------------------------------------------------User New Club Requests relate-------------------------------------------------------"""
"""This method is used to render the user's form for requesting a new Club."""
class ApplyNewClubView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']
    template_name = 'apply_new_club.html'

    def get(self, request):
        form = NewClubRequestForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NewClubRequestForm(request.POST)
        if form.is_valid():
            club_name = form.cleaned_data['name']
            
            if isSameClubNameExist(club_name):
                messages.error(request, "A club with this name already exists.")
                return render(request, self.template_name, {'form': form})
            
            new_request = form.save(commit=False)
            new_request.creator = request.user
            new_request.save()
            
            admins = User.objects.filter(account_type='Admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New Club Request",
                    message=f"A new club request '{new_request.name}' has been submitted. Click 'continue' to check the request.",
                    notification_type='general',
                    url=reverse('admin_panel_new_club_requests_detail' , args=[new_request.request_id])
                )
            
            messages.success(request, "Your club creation request has been submitted and is pending approval.")
            return redirect('dashboard_new_club_requests')
        
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})
"""-------------------------------------------------------User New Club Requests relate end-------------------------------------------------------"""
