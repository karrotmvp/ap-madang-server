from importlib.util import decode_source
from tracemalloc import start
from rest_framework import viewsets, mixins
from datetime import date, timedelta, datetime
from django.db.models import OuterRef, Subquery, Count
from django.db.utils import IntegrityError
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404

from user.jwt_authentication import (
    jwt_authentication,
    jwt_light_authentication,
    jwt_authentication_fbv,
)
from .models import *
from .serializers import *
from .utils import *
from agora.models import *
from oauth.views import get_region_from_region_id
from zoom.views import create_zoom_meeting, delete_zoom_meeting
from alarmtalk.models import UserMeetingAlarm
from share.utils import create_meeting_short_url

from config.settings import CLIENT_BASE_URL


class MeetingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MeetingLogSerializer
    queryset = MeetingLog.objects

    def get_queryset(self):
        if self.request.user is not None:
            queryset = (
                MeetingLog.objects.annotate(
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
                            user=self.request.user,
                            meeting=OuterRef("pk"),
                        ).values("id")
                    )
                )
                .prefetch_related("meeting", "meeting__user")
                .order_by("-date", "-meeting__start_time")
            )

        else:
            queryset = (
                MeetingLog.objects.annotate(
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
                .prefetch_related("meeting", "meeting__user")
                .order_by("-date", "-meeting__start_time")
            )

        if self.action == "list":
            today = date.today()
            region = self.request.region

            queryset = queryset.filter(
                meeting__is_deleted=False,
                meeting__is_link=False,
                date__range=["2022-02-25", today],
                meeting__region=region,
            )
            filtered_queryset = []
            for q in queryset:
                q.live_status = get_live_status(
                    q.date, q.meeting.start_time, q.meeting.end_time
                )
                if q.live_status == "live" or q.live_status == "finish":
                    filtered_queryset.append(q)
            return filtered_queryset

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return MeetingLogSerializer
        return MeetingLogDetailSerializer

    @jwt_light_authentication
    def list(self, request, *args, **kwargs):
        region_id = request.GET.get("region_id", None)
        request.region = get_region_from_region_id(region_id).get("name2")
        # TODO region ?????? ?????? ??? ?????? ??????
        # self.request.data.update({"user": request.user})
        return super().list(request, *args, **kwargs)

    def get_object(self):
        object = super().get_object()
        object.live_status = get_live_status(
            object.date, object.meeting.start_time, object.meeting.end_time
        )
        return object

    @jwt_light_authentication
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        description_format = {"text": request.data.get("description", "")}
        desc = json.dumps(description_format, ensure_ascii=False)
        start_time, end_time = set_start_end_time(request.data.get("start_time", None))

        # image_url = request.data.get("image_url", None)
        self.request.data.update(
            {
                "user": request.user.id,
                "region": request.region,
                # "image": get_meeting_image(image_url),
                "description": desc,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        # self.user_id = request.user.id

        # Meeting Obj Create
        serializer = MeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()

        # MeetingLog Obj Create
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        meeting_log = MeetingLog.objects.create(meeting=meeting, date=date)

        origin_url = "{}/?#/?meeting={}".format(CLIENT_BASE_URL, meeting_log.id)
        url, code = create_meeting_short_url(origin_url, meeting_log.id)
        meeting_log.share_code = code
        meeting_log.save()

        if meeting.is_video:
            meeting.meeting_url = create_zoom_meeting(meeting_log)
            meeting.save()

        # send_meeting_create_alarm_talk(meeting_log)

        # if image_url:
        #     send_image_resize_sqs_msg(meeting.id, image_url)

        send_meeting_create_slack_webhook(meeting_log)
        return Response({"id": meeting_log.id}, status=status.HTTP_201_CREATED)

    @jwt_authentication
    def destroy(self, request, *args, **kwargs):
        meetinglog = self.get_object()
        if meetinglog.meeting.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        meeting = meetinglog.meeting
        meeting.is_deleted = True
        if meeting.is_video:
            delete_zoom_meeting(meeting.meeting_url)

        meeting.save()

        return super().destroy(request, *args, **kwargs)


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

        send_meeting_enter_slack_webhook(
            request.user, MeetingLog.objects.get(id=kwargs["pk"])
        )

        return HttpResponse(status=201)


@api_view(["GET"])
def get_presigned_url(request):
    file_name = request.GET.get("file_name", None)
    url = generate_presigned_url(file_name)
    return Response(url, status=status.HTTP_200_OK)


@api_view(["GET"])
@jwt_authentication_fbv
def get_meeting_agora_user_list(request, pk):
    meeting_log = get_object_or_404(MeetingLog, id=pk)
    return Response(json.loads(meeting_log.agora_user_list), status=status.HTTP_200_OK)


@api_view(["POST"])
@jwt_authentication_fbv
def create_meeting_link(request):
    user = request.user
    region = request.region
    title = "{}?????? ?????? ?????? ???".format(user.nickname)

    meeting = Meeting.objects.create(
        user=user, region=region, title=title, is_link=True
    )
    meeting_log = MeetingLog.objects.create(meeting=meeting)

    origin_url = "{}/daangn?#/redirect?meeting={}".format(
        CLIENT_BASE_URL, meeting_log.id
    )

    url, share_code = create_meeting_short_url(origin_url, meeting_log.id)

    send_meeting_link_create_slack_webhook(meeting_log)

    return Response(
        {"id": meeting_log.id, "share_code": share_code}, status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@jwt_authentication_fbv
def create_meeting_link(request):
    user = request.user
    region = request.region
    title = "{}?????? ?????? ?????? ???".format(user.nickname)

    meeting = Meeting.objects.create(
        user=user, region=region, title=title, is_link=True
    )
    meeting_log = MeetingLog.objects.create(meeting=meeting)

    origin_url = "{}/daangn?#/redirect?meeting={}".format(
        CLIENT_BASE_URL, meeting_log.id
    )

    url, share_code = create_meeting_short_url(origin_url, meeting_log.id)

    send_meeting_link_create_slack_webhook(meeting_log)

    return Response(
        {"id": meeting_log.id, "share_code": share_code}, status=status.HTTP_201_CREATED
    )


# ?????? ?????? ??????
@api_view(["PATCH"])
@jwt_authentication_fbv
def close_meeting_link(request, pk):
    meeting_log = get_object_or_404(MeetingLog, id=pk)

    # ???????????? ??????
    if request.user.id != meeting_log.meeting.user.id:
        return Response(
            {
                "error_message": "????????? ????????? ????????? ??? ????????????",
                "error_code": "CLOSED_NOT_PERMITTED",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # ???????????? ?????? ???????????? ??????
    if meeting_log.closed_at is not None:
        return Response(
            {"error_message": "?????? ????????? ???????????????", "error_code": "ALREADY_CLOSED"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    meeting_log.closed_at = datetime.datetime.now()
    meeting_log.save()

    return Response(status=status.HTTP_200_OK)


# ?????? ?????? ??????
@api_view(["PATCH"])
@jwt_authentication_fbv
def close_meeting(request, pk):
    meeting_log = get_object_or_404(MeetingLog, id=pk)

    # ???????????? ??????
    if request.user.id != meeting_log.meeting.user.id:
        return Response(
            {
                "error_message": "????????? ????????? ????????? ??? ????????????",
                "error_code": "CLOSED_NOT_PERMITTED",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    now = datetime.datetime.now()

    # ?????? ??????????????? ????????? ?????? ?????? ??????(????????? ???????????? ?????? ??????)
    if meeting_log.get_meeting_start_datetime() > now:
        return Response(
            {"error_message": "???????????? ?????? ????????? ????????? ??? ????????????", "error_code": "NOT_STARTED"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ?????? ??????????????? ????????? ?????? ?????? ??????(?????? ????????? ????????? ??????)
    if meeting_log.get_meeting_end_datetime() < now:
        return Response(
            {"error_message": "?????? ????????? ???????????????", "error_code": "ALREADY_CLOSED"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    meeting = Meeting.objects.get(id=meeting_log.meeting.id)
    meeting.end_time = now.time()
    meeting.save()

    return Response(status=status.HTTP_200_OK)
