from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication, jwt_light_authentication
from .models import *
from .serializers import *
from .utils import *
from datetime import date, timedelta, datetime
from django.db.models import OuterRef, Subquery, Count
from django.db.utils import IntegrityError
from django.http import HttpResponse
from agora.models import *
from rest_framework.response import Response
from oauth.views import get_region_from_region_id


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
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MeetingLogSerializer
    queryset = MeetingLog.objects

    def get_queryset(self):
        if self.request.user is not None:
            queryset = (
                MeetingLog.objects.filter(
                    meeting__is_deleted=False,
                    date__in=[date.today(), date.today() + timedelta(days=1)],
                )
                .annotate(
                    user_enter_cnt=Subquery(
                        UserMeetingEnter.objects.filter(meeting=OuterRef("pk"))
                        .values("meeting")
                        .annotate(count=Count("meeting"))
                        .values("count")
                    )
                )
                .annotate(
                    alarm_num=Subquery(
                        UserMeetingAlarm.objects.filter(meeting=OuterRef("pk"))
                        .values("meeting")
                        .annotate(count=Count("meeting"))
                        .values("count")
                    )
                )
                .annotate(
                    alarm_id=Subquery(
                        UserMeetingAlarm.objects.filter(
                            sent_at=None,
                            user=self.request.user.id,
                            meeting=OuterRef("pk"),
                        ).values("id")
                    )
                )
                .select_related("meeting")
                .order_by("date", "meeting__start_time")
            )

        else:
            queryset = (
                MeetingLog.objects.filter(
                    meeting__is_deleted=False,
                    date__in=[date.today(), date.today() + timedelta(days=1)],
                )
                .annotate(
                    user_enter_cnt=Subquery(
                        UserMeetingEnter.objects.filter(meeting=OuterRef("pk"))
                        .values("meeting")
                        .annotate(count=Count("meeting"))
                        .values("count")
                    )
                )
                .annotate(
                    alarm_num=Subquery(
                        UserMeetingAlarm.objects.filter(meeting=OuterRef("pk"))
                        .values("meeting")
                        .annotate(count=Count("meeting"))
                        .values("count")
                    )
                )
                .select_related("meeting")
                .order_by("date", "meeting__start_time")
            )

        if self.action == "list":
            region = self.request.region
            queryset.filter(meeting__region=region)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return MeetingLogSerializer
        return MeetingLogDetailSerializer

    @jwt_light_authentication
    def list(self, request, *args, **kwargs):
        region_id = request.GET.get("region_id", None)
        request.region = get_region_from_region_id(region_id).get("name2")
        # TODO region 문제 있을 때 에러 처리
        self.request.data.update({"user": request.user})
        return super().list(request, *args, **kwargs)

    @jwt_light_authentication
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update(
            {
                "user": request.user.id,
                "region": request.region,
                "start_time": datetime.datetime.strftime(
                    datetime.datetime.now(), "%H:%M:%00"
                ),
            }
        )
        self.user_id = request.user.id

        # Meeting Obj Create
        serializer = MeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()

        # MeetingLog Obj Create
        meeting_log = MeetingLog.objects.create(meeting=meeting, date=date.today())

        # Return Meeting Log Detail
        self.lookup_url_kwarg = "id"
        self.kwargs["id"] = meeting_log.id
        return super().retrieve(request, *args, **kwargs)


class UserMeetingEnterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserMeetingEnterSerializer
    queryset = UserMeetingEnter.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update(
            {"user": request.user.id, "meeting": kwargs["pk"], "region": request.region}
        )
        try:
            super().create(request, *args, **kwargs)
        except IntegrityError:
            pass

        return HttpResponse(status=201)
