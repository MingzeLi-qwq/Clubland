from django.shortcuts import render
from django.views import View
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin


"""以下内容负责渲染Admin Panel"""
class AdminPanelClubs(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/clubs.html')
    
class AdminPanelUsers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/users.html')
    
class AdminPanelEvents(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/events.html')
    
class AdminPanelRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/requests.html')