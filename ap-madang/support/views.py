from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from django.http import HttpResponse, JsonResponse


class UserOpinionViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserOpinionSerializer
    queryset = UserOpinion.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().create(request, *args, **kwargs)


class MeetingReviewViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MeetingReviewSerializer
    queryset = MeetingReview.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().create(request, *args, **kwargs)


def query(request):
    from alarmtalk.models import UserMeetingAlarm
    from meeting.models import UserMeetingEnter, Meeting
    from agora.models import MeetingEnterCode

    res = list()

    meeting_pair = [
        [3, 24],
        [4, 23],
        [5, 22],
        [6, 21],
        [7, 20],
        [8, 19],
        [9, 18],
        [10, 17],
        [11, 16],
        [12, 15],
        [13, 14],
    ]

    for pair in meeting_pair:
        alarms = UserMeetingAlarm.objects.filter(
            meeting__date__range=["2021-11-24", "2021-12-02"],
            meeting__meeting__in=pair
            # meeting__meeting__is_video=False,
        ).exclude(
            user__nickname__in=[
                "찬구",
                "만석닭강정",
                "진희",
                "땅콩",
                "똘빅",
                "당근이당근",
                "양계장",
                "바싹익힌초밥",
                "월화",
                "라면",
            ]
        )

        cnt = 0

        for alarm in alarms:
            if MeetingEnterCode.objects.filter(
                meeting=alarm.meeting, user=alarm.user, is_valid=False
            ).exists():
                cnt += 1

                # if UserMeetingEnter.objects.filter(
                #     meeting=alarm.meeting, user=alarm.user
                # ).exists():
                #     cnt += 1

        print(Meeting.objects.get(id=pair[0]).title)

        print("총 알림 신청자 수", alarms.count())

        print("알림 신청한 사람 중 모임에 입장한 사람", cnt)
        print("알림 신청 -> 모임 입장 전환률", cnt / alarms.count())

        res.append(
            {
                "name": Meeting.objects.get(id=pair[0]).title,
                "총 알림 신청자 수": alarms.count(),
                "알림 신청한 사람 중 모임에 입장한 사람": cnt,
                "전환률": cnt / alarms.count() * 100,
            }
        )

    return JsonResponse(res, status=200, safe=False)
