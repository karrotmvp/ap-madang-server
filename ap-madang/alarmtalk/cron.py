from datetime import datetime
from meeting.models import Meeting
from .models import *
from .views import *


def send_meeting_alarm():
    title = "모임이 시작됐어요"
    text = ""
    primary_button_url = ""
    primary_button_text = "모임 바로가기"
    total_alarm_num = 0

    # 현재 시간에 열리는 모임 리스트 가져오기
    now = datetime.now().time()
    meetings = Meeting.objects.filter(start_time=now)

    # 해당 모임 예약 내역 가져오기
    alarm_list = UserMeetingAlarm.objects.filter(sent_at=None, meeting__in=meetings)

    print("-----user meeting alarm start " + now + " -----")

    for alarm in alarm_list:
        if send_biz_chat_message(
            alarm.user.karrot_user_id,
            title,
            text,
            primary_button_url,
            primary_button_text,
        ):
            alarm.sent_at = datetime.now()
            alarm.save()
            total_alarm_num += 1

        else:
            # TODO 우리한테 노티스 보내기? 아니면 retry 하기?
            pass

    print("-----user meeting alarm end with " + now + " alarm talks total -----")
