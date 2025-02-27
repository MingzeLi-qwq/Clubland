from django.shortcuts import render

def message_dashboard(request):
    return render(request, 'message_system/dashboard.html')