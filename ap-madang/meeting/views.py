from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *

# Create your views here.
class MeetingViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects

    def get_queryset(self):
        region = self.request.region
        return Meeting.objects.filter(is_deleted=False, region=region)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MeetingDetailSerializer
        return MeetingSerializer

    @jwt_authentication
    def list(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().list(request, *args, **kwargs)

    @jwt_authentication
    def retrieve(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().retrieve(request, *args, **kwargs)
