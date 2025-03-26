from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Widget
from .serializers import WidgetSerializer, EventSerializer
from club_system.helpers.mixins import ClubMemberRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.core.files.storage import default_storage
from club_system.models import Club
from event_system.models import Event
from .serializers import EventSerializer



def get_csrf_token(request):
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
class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]
        file_path = default_storage.save(f"uploads/{file.name}", file)

        return Response({"message": "Upload successful", "file_url": file_path}, status=201)

class ClubBackgroundUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)

        background_image = request.data.get("background_image")
        if not background_image:
            return Response({"error": "Missing background_image"}, status=400)
        
        club.background_image = background_image
        club.save()
        return Response({"message": "Background updated successfully!"}, status=200)
class ClubInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        return Response({
            "name": club.name,
            "background_image": club.background_image.url if club.background_image else None
        })

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        club_id = self.request.query_params.get('club_id', None)
        print(f"Received club_id: {club_id}")
        if club_id is not None:
            return Event.objects.filter(club__id=club_id)
        return Event.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@login_required
def club_hub_view(request, club_id):
    user = request.user
    is_admin = user.account_type == 'Admin'
    response = redirect(f'http://51.21.191.188:3000/club-view/{club_id}')
    return response


class ManagerCheckView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, club_id):
        is_manager = Membership.objects.filter(
            user=request.user,
            club_id=club_id,
            is_manager=True
        ).exists()
        return Response({"is_manager": is_manager})
