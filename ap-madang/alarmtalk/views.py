from rest_framework import viewsets, mixins, status
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from rest_framework.response import Response


class UserMeetingAlarmViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserMeetingAlarmSerializer
    queryset = UserMeetingAlarm.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().create(request, *args, **kwargs)

    @jwt_authentication
    def destroy(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        if self.get_object().user.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
