from datetime import datetime, date
from meeting.models import Meeting
from .models import *
from .views import *
from sentry_sdk import capture_message
from config.settings import CLIENT_BASE_URL


def cron_test():
    print("cron job is working!", str(datetime.now()))


def send_meeting_alarm():
    title = "지금 모임이 시작됐어요 🙌"
    text1 = "알림 신청하신 [ "
    text2 = " ] 모임이 시작됐어요.\n아래 '모임 바로가기' 버튼을 눌러 이웃과 대화를 나눠보세요."
    primary_button_text = "모임 바로가기"
    total_alarm_num = 0

    # 현재 시간에 열리는 모임 리스트 가져오기
    now = datetime.strftime(datetime.now(), "%H:%M:%000")
    meetings = MeetingLog.objects.filter(
        meeting__is_deleted=False, meeting__start_time=now, date=date.today()
    )

    # 해당 모임 예약 내역 가져오기
    alarm_list = UserMeetingAlarm.objects.filter(sent_at=None, meeting__in=meetings)
    print("----- user meeting alarm start : " + str(datetime.now()) + " -----")

    for alarm in alarm_list:
        url = "{}/index.html#/redirect?meeting={}&meeting_id={}".format(
            CLIENT_BASE_URL,
            alarm.meeting.meeting.meeting_url[8:],
            str(alarm.meeting.id),
        )
        print(url)
        if send_biz_chat_message(
            alarm.user.karrot_user_id,
            title,
            text1 + alarm.meeting.meeting.title + text2,
            url,
            primary_button_text,
        ):
            print("Alarm sent! to ", alarm.user.karrot_user_id)
            alarm.sent_at = datetime.now()
            alarm.save()
            total_alarm_num += 1

        else:
            capture_message(
                "모임 시작 알림톡이 전송되지 않았습니다. usermeetingalarm.id = " + str(alarm.id)
            )

    print(
        "----- user meeting alarm end with : "
        + str(datetime.now())
        + " alarm talks total ",
        total_alarm_num,
        "-----",
    )
    print()
