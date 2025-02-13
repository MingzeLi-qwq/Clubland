from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Widget
from .serializers import WidgetSerializer
from club_system.helpers.mixins import ClubMemberRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class WidgetViewSet(viewsets.ModelViewSet):
    serializer_class = WidgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Widget.objects.filter(club_id=self.kwargs['club_id'])

    def perform_create(self, serializer):
        serializer.save(club_id=self.kwargs['club_id'])

    @action(detail=False, methods=["POST"])
    def update_layout(self, request, club_id=None):
        layout = request.data.get("layout", [])
        for item in layout:
            widget = Widget.objects.filter(id=item["id"], club_id=club_id).first()
            if widget:
                widget.x = item["x"]
                widget.y = item["y"]
                widget.width = item["width"]
                widget.height = item["height"]
                widget.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


@login_required
def club_dashboard(request, club_id):
    return render(request, "club_hub/dashboard.html", {"club_id": club_id})
