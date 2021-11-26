from rest_framework import viewsets, mixins, status
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from rest_framework.response import Response
from config.settings import API_KEY, BASE_URL_REGION, CLIENT_BASE_URL
import json
import requests
from django.db.utils import IntegrityError
from sentry_sdk import capture_message
from datetime import datetime


def send_biz_chat_message(
    user_id,
    title,
    text,
    primary_button_url,
    primary_button_text,
    image_url,
    is_normal_button,
    normal_button_url=None,
    normal_button_text=None,
):
    url = BASE_URL_REGION + "/api/v2/chat/send_biz_chat_message"

    actions = [
        {
            "payload": {
                "text": primary_button_text,
                "linkUrl": primary_button_url,
            },
            "type": "PRIMARY_BUTTON",
        }
    ]

    if is_normal_button:
        actions.append(
            {
                "payload": {"text": normal_button_text, "linkUrl": normal_button_url},
                "type": "NORMAL_BUTTON",
            }
        )

    payload = {
        "input": {
            "actions": actions,
            "userId": user_id,
            "title": title,
            "text": text,
            "imageUrl": image_url,
        }
    }
    headers = {
        "Accept": "application/json",
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    request_data = json.loads(response.text).get("data", None)

    if request_data is None:
        print("***** Alarm talk sent failed!!! *****")
        print(response.text)
        return False

    return request_data.get("sendBizChatMessage", None).get("status", None) == "OK"


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
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "이미 해당 유저가 해당 모임에 대한 알람을 신청한 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @jwt_authentication
    def destroy(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        if self.get_object().user.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "알람 신청한 유저만이 알람을 해제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
        )


def send_meeting_start_alarm_talk(alarm_list):
    title = "지금 모임이 시작됐어요 🙌"
    text1 = "알림 신청하신 [ "
    text2 = " ] 모임이 시작됐어요.\n아래 '모임 바로가기' 버튼을 눌러 이웃과 대화를 나눠보세요."
    primary_button_text = "모임 바로가기"
    normal_button_url = "{}/index.html?#/".format(
        CLIENT_BASE_URL,
    )
    normal_button_text = "랜동모 홈으로 가기"
    total_alarm_num = 0

    print("----- user meeting start alarm start : " + str(datetime.now()) + " -----")

    for alarm in alarm_list:
        url = "{}/index.html?#/meetings/{}".format(
            CLIENT_BASE_URL, str(alarm.meeting.id)
        )
        if send_biz_chat_message(
            alarm.user.karrot_user_id,
            title,
            text1 + alarm.meeting.meeting.title + text2,
            url,
            primary_button_text,
            alarm.meeting.meeting.image.url,
            True,
            normal_button_url,
            normal_button_text,
        ):
            print(
                "Meeting Start Alarm sent! to id: {}, nickname: {}, karrot_id: {}".format(
                    alarm.user.id, alarm.user.nickname, alarm.user.karrot_user_id
                )
            )
            alarm.sent_at = datetime.now()
            alarm.save()
            total_alarm_num += 1

        else:
            capture_message(
                "모임 시작 알림톡이 전송되지 않았습니다. usermeetingalarm.id = " + str(alarm.id), "error"
            )

    print(
        "----- user meeting start alarm end with : "
        + str(datetime.now())
        + " alarm talks total ",
        total_alarm_num,
        "-----",
    )
    print()
    return total_alarm_num


def send_meeting_end_alarm_talk(enter_list):
    title = "모임은 어떠셨나요? 😊"
    text1 = "참여하신 [ "
    text2 = " ] 모임에 대한 사용자분의 후기를 듣고 싶어요. \n아래 아래 버튼을 눌러 의견을 남겨주세요."
    primary_button_text = "의견 보내러 가기"
    total_alarm_num = 0
    url = "towneers://web/ad/user_surveys/5450"
    meeting_review_image = "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/%EC%95%8C%EB%A6%BC%ED%86%A1.png"

    print(
        "----- user meeting end/review alarm start : " + str(datetime.now()) + " -----"
    )

    for enter in enter_list:
        if send_biz_chat_message(
            enter.user.karrot_user_id,
            title,
            text1 + enter.meeting.meeting.title + text2,
            url,
            primary_button_text,
            meeting_review_image,
            False,
        ):
            print(
                "Meeting End Alarm sent! to id: {}, nickname: {}, karrot_id: {}".format(
                    enter.user.id, enter.user.nickname, enter.user.karrot_user_id
                )
            )
            enter.meeting_review_alarm_sent_at = datetime.now()
            enter.save()
            total_alarm_num += 1

        else:
            capture_message(
                "모임 종료/후기 알림톡이 전송되지 않았습니다. usermeetingenter.id = " + str(enter.id),
                "error",
            )

    print(
        "----- user meeting end/review alarm end with : "
        + str(datetime.now())
        + " alarm talks total ",
        total_alarm_num,
        "-----",
    )
    print()
    return total_alarm_num
