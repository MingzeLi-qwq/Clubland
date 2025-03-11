from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Widget
from .serializers import WidgetSerializer
from club_system.helpers.mixins import ClubMemberRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import get_token


def get_csrf_token(request):
    """
    获取新的CSRF令牌
    """
    return JsonResponse({"csrfToken": get_token(request)})

class WidgetViewSet(viewsets.ModelViewSet):
    serializer_class = WidgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Widget.objects.filter(club_id=self.kwargs['club_id'])

    def perform_create(self, serializer):
        serializer.save(club_id=self.kwargs['club_id'])

    def destroy(self, request, *args, **kwargs):
        widget = self.get_object()
        widget.delete()
        return Response({"message": "组件删除成功"}, status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=["POST"])
    def update_layout(self, request, club_id=None):
        """✅ 更新组件布局"""
        layout = request.data.get("layout", [])

        if not layout:
            return Response({"error": "No layout data provided"}, status=status.HTTP_400_BAD_REQUEST)

        updated_widgets = []
        for item in layout:
            widget = Widget.objects.filter(id=item["i"], club_id=club_id).first()
            if widget:
                widget.x = item["x"]
                widget.y = item["y"]
                widget.width = item["w"]
                widget.height = item["h"]
                widget.save()
                updated_widgets.append(widget.id)

        return Response({"updated": updated_widgets}, status=status.HTTP_200_OK)


@login_required
def club_dashboard(request, club_id):
    return render(request, "club_hub/dashboard.html", {"club_id": club_id})
