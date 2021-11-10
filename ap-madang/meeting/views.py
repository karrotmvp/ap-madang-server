from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from .utils import *
from datetime import date, timedelta
from django.db.models import OuterRef, Subquery, Count


# def get_meeting_list_for_bot(request):
#     if request.method == "GET":
#         meeting_in_24_list = list()

#         meetings = MeetingLog.objects.filter(
#             meeting__is_deleted=False,
#             date__in=[date.today(), date.today() + timedelta(days=1)],
#         )

#         now = datetime.now()

#         for meeting in meetings:
#             if (
#                 timedelta(hours=0)
#                 < datetime.combine(meeting.date, meeting.meeting.start_time) - now
#                 < timedelta(hours=24)
#             ):
#                 dic = {
#                     "title": meeting.meeting.title,
#                     "start_time": meeting.meeting.start_time,
#                     "end_time": meeting.meeting.end_time,
#                     "meeting_url": meeting.meeting.meeting_url,
#                     "region": meeting.meeting.region,
#                     "date": meeting.date,
#                 }
#                 meeting_in_24_list.append(dic)

#         return JsonResponse(meeting_in_24_list, status=200, safe=False)


# Create your views here.
class MeetingViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = MeetingLogSerializer
    queryset = MeetingLog.objects

    def get_queryset(self):
        region = self.request.region
        return (
            MeetingLog.objects.filter(
                meeting__is_deleted=False,
                meeting__region=region,
                date__in=[date.today(), date.today() + timedelta(days=1)],
            )
            .annotate(
                user_enter_cnt=Subquery(
                    UserMeetingEnter.objects.filter(meeting=OuterRef("pk"))
                    .values("meeting")
                    .annotate(count=Count("meeting"))
                    .values("count")
                ),
            )
            .select_related("meeting")
            .order_by("date", "meeting__start_time")
        )

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
        # TODO 중복 제거
        return super().create(request, *args, **kwargs)
