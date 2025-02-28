from django.shortcuts import render

def message_dashboard(request):
    return render(request, 'messages/message_dashboard.html')