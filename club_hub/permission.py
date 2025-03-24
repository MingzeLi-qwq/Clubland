from rest_framework.permissions import BasePermission
from club_system.models import Membership

class IsClubMember(BasePermission):
    def has_permission(self, request, view):
        club_id = view.kwargs.get('club_id')
        return Membership.objects.filter(user=request.user, club_id=club_id).exists()
