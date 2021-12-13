from rest_framework import viewsets, mixins, status
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *
from rest_framework.response import Response
from config.settings import API_KEY, BASE_URL_REGION
import json
import requests
from django.db.utils import IntegrityError
from sentry_sdk import capture_message
from datetime import datetime
from .utils import *


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
    normal_button_url = get_home_client_page()
    normal_button_text = "랜동모 홈으로 가기"
    total_alarm_num = 0

    for alarm in alarm_list:
        url = get_meeting_detail_client_page(alarm.meeting.id)
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
                "[Meeting Start Alarm] sent to id: {}, nickname: {}, karrot_id: {}".format(
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

    return total_alarm_num


def send_meeting_end_alarm_talk(enter_list):
    title = "모임은 어떠셨나요? 😊"
    text1 = "참여하신 [ "
    text2 = " ] 모임에 대한 사용자분의 후기를 듣고 싶어요. \n아래 아래 버튼을 눌러 의견을 남겨주세요."
    primary_button_text = "의견 보내러 가기"
    total_alarm_num = 0
    url = "towneers://web/ad/user_surveys/5450"
    meeting_review_image = "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/alarmtalk_meeting_review.png"

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
                "[Meeting End Alarm] sent to id: {}, nickname: {}, karrot_id: {}".format(
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

    return total_alarm_num


def send_meeting_start_alarm_talk_to_owners(meetinglog_list):
    title = "지금 모임이 시작됐어요 🙌"
    text1 = "개설하신 [ "
    text2 = " ] 모임이 시작됐어요.\n아래 '모임 바로가기' 버튼을 눌러 이웃과 대화를 나눠보세요."
    primary_button_text = "모임 바로가기"
    normal_button_url = get_home_client_page()
    normal_button_text = "랜동모 홈으로 가기"
    total_alarm_num = 0

    for meetinglog in meetinglog_list:
        if meetinglog.meeting.user:
            url = get_meeting_detail_client_page(meetinglog.id)
            if send_biz_chat_message(
                meetinglog.meeting.user.karrot_user_id,
                title,
                text1 + meetinglog.meeting.title + text2,
                url,
                primary_button_text,
                meetinglog.meeting.image.url,
                True,
                normal_button_url,
                normal_button_text,
            ):
                print(
                    "[Meeting Start Owner Alarm] sent to id: {}, nickname: {}, karrot_id: {}".format(
                        meetinglog.meeting.user.id,
                        meetinglog.meeting.user.nickname,
                        meetinglog.meeting.user.karrot_user_id,
                    )
                )
                total_alarm_num += 1

            else:
                capture_message(
                    "모임 시작 알림톡이 전송되지 않았습니다. meetinglog.id = " + str(meetinglog.id),
                    "error",
                )

    return total_alarm_num


# def send_meeting_create_alarm_talk(meetinglog):
#     title = "모임이 개설됐어요 🥳"
#     datetime_in_korean = date_and_time_to_korean(
#         datetime.strptime(meetinglog.date, "%Y-%m-%d").date(),
#         meetinglog.meeting.start_time,
#     )
#     text = "[ {} ] 모임이 개설되어, 이웃들의 알림 신청을 기다리고 있어요.\n실시간으로 모임 알림 신청 현황을 확인해보세요.\n\n모임 시작 일시 : {}".format(
#         meetinglog.meeting.title, datetime_in_korean
#     )
#     primary_button_text = "모임 바로가기"
#     normal_button_url = get_home_client_page()
#     normal_button_text = "랜동모 홈으로 가기"

#     url = get_meeting_detail_client_page(meetinglog.id)

#     if meetinglog.meeting.user:
#         if send_biz_chat_message(
#             meetinglog.meeting.user.karrot_user_id,
#             title,
#             text,
#             url,
#             primary_button_text,
#             meetinglog.meeting.image.url,
#             True,
#             normal_button_url,
#             normal_button_text,
#         ):
#             print(
#                 "Meeting Create Alarm sent! to id: {}, nickname: {}, karrot_id: {}".format(
#                     meetinglog.meeting.user.id,
#                     meetinglog.meeting.user.nickname,
#                     meetinglog.meeting.user.karrot_user_id,
#                 )
#             )

#         else:
#             capture_message(
#                 "모임 생성 알림톡이 전송되지 않았습니다. meetinglog.id = " + str(meetinglog.id),
#                 "error",
#             )


def send_meeting_create_function_alarm_talk_to_opinions(opinion_list):
    title = "제안하신 모임을 지금 만들어보세요!🥳"
    text = "이제 랜선동네모임에서 모임을 만들 수 있어요.\n랜동모에서 이웃과 함께하고 싶었던 모임을, 지금 만들어보세요"
    primary_button_text = "모임 생성하러 가기"
    total_alarm_num = 0
    url = get_home_client_page()
    meeting_create_image = "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/alarmtalk_meeting_create.png"

    for opinion in opinion_list:
        if send_biz_chat_message(
            opinion.user.karrot_user_id,
            title,
            text,
            url,
            primary_button_text,
            meeting_create_image,
            False,
        ):
            print(
                "[Meeting Create Function] sent to id: {}, nickname: {}, karrot_id: {}".format(
                    opinion.user.id, opinion.user.nickname, opinion.user.karrot_user_id
                )
            )
            opinion.sent_at = datetime.now()
            opinion.save()
            total_alarm_num += 1

        else:
            capture_message(
                "모임 생성 기능 알림톡이 전송되지 않았습니다. useropinion.id = " + str(opinion.id),
                "error",
            )

    return total_alarm_num


def send_welcome_alarm_talk_to_new_user(user):
    title = "{}님, 랜선동네모임에 오신 것을 환영해요🤗"
    text = "동네 이웃을 만나는 공간 '랜선동네모임'에서 이웃들과 대화를 나눠보세요! \n아래 '랜동모 홈으로 가기' 버튼을 눌러 우리 동네 모임을 둘러보세요. "
    primary_button_text = "랜동모 홈으로 가기"
    url = get_home_client_page()
    welcome_image = "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/alarmtalk_welcome.png"

    if send_biz_chat_message(
        user.karrot_user_id,
        title.format(user.nickname),
        text,
        url,
        primary_button_text,
        welcome_image,
        False,
    ):
        print(
            "[Welcome To New Users] sent to id: {}, nickname: {}, karrot_id: {}".format(
                user.id, user.nickname, user.karrot_user_id
            )
        )
        user.sent_at = datetime.now()
        user.save()

    else:
        capture_message(
            "새 유저 환영 알림톡이 전송되지 않았습니다. useropinion.id = " + str(user.id),
            "error",
        )


def send_meeting_start_in_hour_alarm_talk(alarm_list):
    title = "한 시간 뒤에 모임이 시작돼요 ⏰"
    text = "알림 신청하신 [ {} ] 모임이 한 시간 뒤에 시작돼요.\n이웃과의 즐거운 만남이 기다리고 있으니 {}에 만나요🤗"
    primary_button_text = "모임 바로가기"
    normal_button_url = get_home_client_page()
    normal_button_text = "랜동모 홈으로 가기"
    total_alarm_num = 0

    for alarm in alarm_list:
        url = get_meeting_detail_client_page(alarm.meeting.id)
        if send_biz_chat_message(
            alarm.user.karrot_user_id,
            title,
            text.format(
                alarm.meeting.meeting.title,
                time_to_korean(alarm.meeting.meeting.start_time, twelve_base=True),
            ),
            url,
            primary_button_text,
            alarm.meeting.meeting.image.url,
            True,
            normal_button_url,
            normal_button_text,
        ):
            print(
                "[Meeting Start in Hour Alarm] sent to id: {}, nickname: {}, karrot_id: {}".format(
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

    return total_alarm_num


def send_meeting_start_in_hour_alarm_talk_to_owners(meetinglog_list):
    title = "한 시간 뒤에 모임이 시작돼요 ⏰"
    text = "개설하신 [ {} ] 모임이 한 시간 뒤에 시작돼요.\n이웃과의 즐거운 만남이 기다리고 있으니 {}에 만나요🤗"
    primary_button_text = "모임 바로가기"
    normal_button_url = get_home_client_page()
    normal_button_text = "랜동모 홈으로 가기"
    total_alarm_num = 0

    for meetinglog in meetinglog_list:
        if meetinglog.meeting.user:
            url = get_meeting_detail_client_page(meetinglog.id)
            if send_biz_chat_message(
                meetinglog.meeting.user.karrot_user_id,
                title,
                text.format(
                    meetinglog.meeting.title,
                    time_to_korean(meetinglog.meeting.start_time, twelve_base=True),
                ),
                url,
                primary_button_text,
                meetinglog.meeting.image.url,
                True,
                normal_button_url,
                normal_button_text,
            ):
                print(
                    "[Meeting Start in Hour Owner Alarm] sent to id: {}, nickname: {}, karrot_id: {}".format(
                        meetinglog.meeting.user.id,
                        meetinglog.meeting.user.nickname,
                        meetinglog.meeting.user.karrot_user_id,
                    )
                )
                total_alarm_num += 1

            else:
                capture_message(
                    "모임 시작 알림톡이 전송되지 않았습니다. meetinglog.id = " + str(meetinglog.id),
                    "error",
                )

    return total_alarm_num
