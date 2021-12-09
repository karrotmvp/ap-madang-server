from rest_framework.decorators import api_view
import json
from config.settings import JWT_SECRET
from oauth.views import (
    get_access_token_from_code,
    get_user_info,
    get_region_from_region_id,
    get_manner_temperature,
)
from django.http import HttpResponse, JsonResponse
from .models import User
from .serializers import UserSerializer
import jwt
from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication
from meeting.models import MeetingLog, UserMeetingEnter
from alarmtalk.models import UserMeetingAlarm
from meeting.serializers import MeetingLogSerializer
from django.db.models import OuterRef, Subquery, Count
from .utils import *
from meeting.utils import *
from alarmtalk.views import send_welcome_alarm_talk_to_new_user


@api_view(["POST"])
def login(request):
    code = json.loads(request.body)["code"]
    region_id = json.loads(request.body)["region_id"]
    # TODO body 값 없을 때 -> 404 Not Found

    # get access token
    access_token = get_access_token_from_code(code)
    if access_token is None:
        return HttpResponse(status=401)

    # get user info
    user_info = get_user_info(access_token)
    if user_info is None:
        return HttpResponse(status=401)

    karrot_user_id = user_info.get("user_id", None)
    nickname = user_info.get("nickname", None)
    profile_image_url = user_info.get("profile_image_url", None)
    manner_temperature = get_manner_temperature(karrot_user_id)

    # 지역(구) 정보 가져오기
    region_data = get_region_from_region_id(region_id)
    region_name = region_data.get("name")
    region_name2 = region_data.get("name2")
    # TODO region 문제 있을 때 에러 처리

    user, created = User.objects.update_or_create(
        karrot_user_id=karrot_user_id,
        defaults={
            "nickname": nickname,
            "profile_image_url": profile_image_url,
            "manner_temperature": manner_temperature,
            "region_name": region_name,
        },
    )

    token = jwt.encode(
        {
            "nickname": nickname,
            "region": region_name2,
            "code": code,
            "profile_image_url": get_profile_image_url(user),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    user.token = token
    user.save()

    if created:
        send_welcome_alarm_talk_to_new_user(user)

    return JsonResponse({"token": token}, status=200, safe=False)


class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects

    @jwt_authentication
    def retrieve(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().retrieve(request, *args, **kwargs)

    # def get_queryset(self):
    #     user_ids = [int(s) for s in self.request.query_params.get("ids").split(",")]
    #     return User.objects.filter(id__in=user_ids)


class UserMeetingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = MeetingLogSerializer
    queryset = MeetingLog.objects

    def get_queryset(self):
        queryset = (
            MeetingLog.objects.filter(
                meeting__is_deleted=False, meeting__user=self.request.user.id
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
            .order_by("-date", "-meeting__start_time")
        )

        filtered_queryset = []
        for q in queryset:
            q.live_status = get_live_status(
                q.date, q.meeting.start_time, q.meeting.end_time
            )
            if q.live_status != "finish":
                filtered_queryset.append(q)
        return filtered_queryset

    @jwt_authentication
    def list(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().list(request, *args, **kwargs)
