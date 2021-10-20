from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from .utils import *

# Create your views here.
class MeetingViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects

    def get_queryset(self):
        region = self.request.region
        return MeetingLog.objects.filter(
            meeting__is_deleted=False,
            meeting__region=region,
            date__in=[date.today(), date.today() + timedelta(days=1)],
        ).order_by("date", "meeting__start_time")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MeetingLogDetailSerializer
        return MeetingLogSerializer

    @jwt_authentication
    def list(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().list(request, *args, **kwargs)

    @jwt_authentication
    def retrieve(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().retrieve(request, *args, **kwargs)


class UserMeetingEnterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserMeetingEnterSerializer
    queryset = UserMeetingEnter.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update(
            {"user": request.user.id, "meeting": kwargs["pk"], "region": request.region}
        )
        return super().create(request, *args, **kwargs)
