from rest_framework import viewsets, mixins
from datetime import date, timedelta
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
                .order_by("date", "meeting__start_time")
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
                .prefetch_related("meeting")
                .order_by("date", "meeting__start_time")
            )

        if self.action == "list":
            today = date.today()
            region = self.request.region

            queryset = queryset.filter(
                meeting__is_deleted=False,
                meeting__is_link=False,
                date__range=(today - timedelta(days=1), today + timedelta(days=6)),
                meeting__region=region,
            ).exclude(
                date__range=(today + timedelta(days=2), today + timedelta(days=6)),
                meeting__user__isnull=True,
            )
            filtered_queryset = []
            for q in queryset:
                q.live_status = get_live_status(
                    q.date, q.meeting.start_time, q.meeting.end_time
                )
                if q.live_status != "finish":
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
        # TODO region 문제 있을 때 에러 처리
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
        desc = json.dumps(request.data.get("description", None), ensure_ascii=False)
        image_url = request.data.get("image_url", None)
        self.request.data.update(
            {
                "user": request.user.id,
                "region": request.region,
                "image": get_meeting_image(image_url),
                "description": desc,
            }
        )
        # self.user_id = request.user.id

        # Meeting Obj Create
        serializer = MeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.save()

        # MeetingLog Obj Create
        date = request.data["date"]
        meeting_log = MeetingLog.objects.create(meeting=meeting, date=date)

        if meeting.is_video:
            meeting.meeting_url = create_zoom_meeting(meeting_log)
            meeting.save()

        # send_meeting_create_alarm_talk(meeting_log)

        if image_url:
            send_image_resize_sqs_msg(meeting.id, image_url)

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
    title = "{}님의 음성 모임 방".format(user.nickname)

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
    title = "{}님의 음성 모임 방".format(user.nickname)

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


@api_view(["PATCH"])
@jwt_authentication_fbv
def close_meeting_link(request, pk):
    meeting_log = get_object_or_404(MeetingLog, id=pk)

    # 방장인지 확인
    if request.user.id != meeting_log.meeting.user.id:
        return Response(
            {
                "error_message": "방장만 모임을 종료할 수 있습니다",
                "error_code": "CLOSED_NOT_PERMITTED",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # 종료되지 않은 모임인지 확인
    if meeting_log.closed_at is not None:
        return Response(
            {"error_message": "이미 종료된 모임입니다", "error_code": "ALREADY_CLOSED"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    meeting_log.closed_at = datetime.datetime.now()
    meeting_log.save()

    return Response(status=status.HTTP_200_OK)
