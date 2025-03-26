from django.shortcuts import get_object_or_404, render
from django.views import View
from django.db.models import Q
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from notification_system.models import Notification
from event_system.models import Event, Category, RSVP


def verifyAdminPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            # Password Verification Successful
            request.session['password_verified'] = True
            if request.session.get('pending_action') == 'delete_club':
                club_id = request.session.get('club_id')
                return redirect('admin_delete_club', club_id=club_id)
            elif request.session.get('pending_action') == 'delete_event':
                club_id = request.session.get('club_id')
                event_id = request.session.get('event_id')
                return redirect('delete_event', event_id=event_id, club_id=club_id)
            return redirect(request.session.get('return_url', 'admin_panel_clubs'))
        else:
            messages.error(request, 'Wrong password, please try again.')
    
    return render(request, 'verify_password.html')


"""-----------------------------------------The following are responsible for rendering the Admin Panel---------------------------------------------------"""
class AdminPanelClubs(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        if search_query:
            clubs = Club.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
        else:
            clubs = Club.objects.all()
        
        club_count = Club.objects.all().count()
        return render(request, 'admin_panel/clubs.html', {
            'clubs': clubs,
            'club_count': club_count,
            'search_query': search_query,
        })
    
class AdminPanelUsers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        if search_query:
            users = User.objects.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query),
                account_type=User.ACCOUNT_TYPE_USER
            )
        else:
            users = User.objects.filter(account_type=User.ACCOUNT_TYPE_USER)
        
        user_count = User.objects.all().count()
        return render(request, 'admin_panel/users.html', {
            'users': users,
            'user_count': user_count,
            'search_query': search_query,
        })
    
class AdminPanelAdminUsers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        if search_query:
            admin_users = User.objects.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query),
                account_type=User.ACCOUNT_TYPE_ADMIN
            )
        else:
            admin_users = User.objects.filter(account_type=User.ACCOUNT_TYPE_ADMIN)
        
        user_count = User.objects.filter(account_type=User.ACCOUNT_TYPE_ADMIN).count()
        return render(request, 'admin_panel/admin_users.html', {
            'admin_users': admin_users,
            'admin_user_count': user_count,
            'search_query': search_query,
        })

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('admin_panel_admin_users')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username {username} already exists")
            return redirect('admin_panel_admin_users')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email {email} is already registered")
            return redirect('admin_panel_admin_users')

        try:
            User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password1,
                account_type=User.ACCOUNT_TYPE_ADMIN
            )
            messages.success(request, f"Admin user {username} created successfully")
        except IntegrityError as e:
                messages.error(request, "Error creating user")
        
        return redirect('admin_panel_admin_users')
    
class AdminPanelRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):        
        return render(request, 'admin_panel/requests.html')
"""-----------------------------------------The above is responsible for rendering Admin Panel---------------------------------------------------"""






"""-----------------------------------------The following is responsible for rendering Admin Panel Club---------------------------------------------------"""
class AdminPanelClubsGeneral(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/general.html", {
            'club':club,
            'club_id':club_id,
        })
    
class AdminPanelClubsMembers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
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

        return render(request, "admin_panel/admin_panel_club/members.html", {
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
    
class AdminPanelClubsNews(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/news.html", {
            'club':club,
            'club_id':club_id,
        })

class AdminPanelClubsForum(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/forum.html", {
            'club':club,
            'club_id':club_id,
        })

    
class AdminPanelClubsDashboard(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/dashboard.html", {
            'club':club,
            'club_id':club_id,
        })


class AdminPanelClubsEvents(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

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
        return render(request, 'admin_panel/admin_panel_club/events.html', context)
    

class AdminDeleteClub(LoginRequiredMixin, UserTypeRequiredMixin, View):
    """Processing requests to delete clubs"""
    allowed_types = ['Admin']

    def get(self, request, club_id):
        if request.session.get('password_verified'):
            del request.session['password_verified']
            club = get_object_or_404(Club, pk=club_id)
            club_name = club.name
            managers = Membership.objects.filter(club=club, is_manager=True).select_related('user')

            # Send notifications to all administrators
            for membership in managers:
                Notification.objects.create(
                    user=membership.user,
                    title="Club Deleted",
                    message=f"The club '{club_name}' has been deleted by an administrator.",
                    notification_type='general',
                )

            club.delete()
            
            messages.success(request, f"Club '{club_name}' has been deleted")
            return redirect('admin_panel_clubs')
        else:
            return redirect('verify_admin_password')

    def post(self, request, club_id):
        if not request.session.get('password_verified'):
            request.session['return_url'] = reverse('admin_panel_club_general', kwargs={'club_id': club_id})
            request.session['pending_action'] = 'delete_club'
            request.session['club_id'] = club_id
            return redirect('verify_admin_password')
        else:
            return self.get(request, club_id)
"""-----------------------------------------The above is Responsible for rendering Admin Panel Club---------------------------------------------------"""



"""-----------------------------------------The following is responsible for rendering the Admin Panel Club Event---------------------------------------------------"""
class AdminPanelClubsEventGeneral(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, event_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, pk=event_id)
        all_categories = Category.objects.all()
        return render(request, "admin_panel/admin_panel_club/admin_panel_club_event/general.html", {
            'club': club,
            'event': event,
            'club_id': club_id,
            'event_id': event_id,
            'all_categories': all_categories,
        })

class AdminPanelClubsEventRSVPs(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, event_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, pk=event_id)
        
        # search functionality
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
        return render(request, "admin_panel/admin_panel_club/admin_panel_club_event/RSVPs.html", context)
"""-----------------------------------------The above is Responsible for rendering Admin Panel Club Event---------------------------------------------------"""







"""-----------------------------------------The following are responsible for rendering Admin Panel User---------------------------------------------------"""
class AdminPanelUserInformation(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, username, *args, **kwargs):
        panel_user = get_object_or_404(User, username=username)
        return render(request, "admin_panel/admin_panel_user/information.html", {
            'panel_user':panel_user,
            'panel_username':username,
        })

class AdminPanelUserMemberships(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    
    def get(self, request, username, *args, **kwargs):
        panel_user = get_object_or_404(User, username=username)
        search_query = request.GET.get('search', '')
        
        memberships = Membership.objects.filter(user=panel_user)
        if search_query:
            memberships = memberships.filter(
                Q(club__name__icontains=search_query)
            )
        
        managers = memberships.filter(is_manager=True).order_by('-date_joined')
        regulars = memberships.filter(is_manager=False).order_by('-date_joined')
        
        return render(request, "admin_panel/admin_panel_user/memberships.html", {
            'panel_user': panel_user,
            'panel_username': username,
            'managers': managers,
            'regulars': regulars,
            'manager_count': managers.count(),
            'regular_count': regulars.count(),
            'search_query': search_query,
        })

class AdminPanelRemoveMemberships(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    
    def post(self, request, username, club_id):
        
        # 执行删除
        membership = get_object_or_404(Membership, user__username=username, club__club_id=club_id)
        club_name = membership.club.name
        membership.delete()
        
        messages.success(request, f"Removed membership from {club_name}")
        return redirect('admin_panel_user_memberships', username=username)

"""-----------------------------------------The above is responsible for rendering Admin Panel User---------------------------------------------------"""


"""-----------------------------------------The following is responsible for rendering the Admin Panel Request---------------------------------------------------"""
class AdminPanelNewClubRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        
        pending_ncRequests = NewClubRequest.objects.filter(status='pending')
        finished_ncRequests = NewClubRequest.objects.filter(Q(status='approved') | Q(status='rejected'))
        
        if search_query:
            pending_ncRequests = pending_ncRequests.filter(name__icontains=search_query)
            finished_ncRequests = finished_ncRequests.filter(name__icontains=search_query)
        
        context = {
            'search_query': search_query,
            'pending_ncRequests': pending_ncRequests,
            'finished_ncRequests': finished_ncRequests,
            'pending_count': pending_ncRequests.count(),
            'finished_count': finished_ncRequests.count(),
        }
        
        return render(request, 'admin_panel/admin_panel_requests/new_club_requests.html', context)


class AdminPanelNewClubRequestDetail(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, ncRequest_id, *args, **kwargs):
        ncRequest = get_object_or_404(NewClubRequest, request_id=ncRequest_id)
        creator = ncRequest.creator
        context = {
            'ncRequest': ncRequest,
            'creator':creator
        }
        return render(request, 'admin_panel/admin_panel_requests/new_club_request_detail.html', context)
    

class AdminReviewNewClubRequest(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, request_id, *args, **kwargs):
        ncRequest = get_object_or_404(NewClubRequest, request_id=request_id)
        return render(request, 'admin_panel/admin_panel_requests/new_club_request_detail.html', {'ncRequest': ncRequest})

    def post(self, request, request_id, *args, **kwargs):
        ncRequest = get_object_or_404(NewClubRequest, request_id=request_id)
        action = request.POST.get('action')
        review_text = request.POST.get('review')

        ncRequest.reviewed_at = timezone.now()
        ncRequest.reviewed_by = request.user
        ncRequest.review = review_text

        if action == 'accept':
            new_club = Club.objects.create(
                name=ncRequest.name,
                description=ncRequest.description
            )
            Membership.objects.create(
                user=ncRequest.creator,
                club=new_club,
                is_manager=True
            )
            ncRequest.status = NewClubRequest.STATUS_APPROVED
            # send notification
            Notification.objects.create(
                user=ncRequest.creator,
                title="New Club Request Accepted",
                message=f"Your club request '{ncRequest.name}' has been approved. Click 'continue' to check your club detail",
                notification_type='general',
                url=reverse('club_detail', args=[new_club.club_id])
            )
            messages.success(request, f"Club request '{ncRequest.name}' has been approved and the club has been created.")
        elif action == 'reject':
            Notification.objects.create(
                user=ncRequest.creator,
                title="New Club Request Rejected",
                message=f"Your club request '{ncRequest.name}' has been rejected.",
                notification_type='general'
            )
            ncRequest.status = NewClubRequest.STATUS_REJECTED
            messages.success(request, f"Club request '{ncRequest.name}' has been rejected.")

        ncRequest.save()

        return redirect('admin_panel_new_club_requests')

    
"""-----------------------------------------The above is responsible for rendering Admin Panel Request---------------------------------------------------"""