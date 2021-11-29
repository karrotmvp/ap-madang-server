from meeting.models import UserMeetingEnter
from .models import *
from .views import *
from datetime import date, timedelta
from django.db.models import F


def send_meeting_alarm():
    now = datetime.strftime(datetime.now(), "%H:%M:%000")

    # 현재 시간에 열리는 모임 리스트 가져오기
    meetings = MeetingLog.objects.filter(
        meeting__is_deleted=False, meeting__start_time=now, date=date.today()
    )

    # 해당 모임 예약 내역 가져오기
    alarm_list = UserMeetingAlarm.objects.filter(sent_at=None, meeting__in=meetings)

    # 오픈 알람톡 보내기
    send_meeting_start_alarm_talk(alarm_list)

    # 현재 시간에 끝나는 모임 리스트 가져오기
    meetings_today = MeetingLog.objects.filter(
        meeting__is_deleted=False, meeting__end_time=now, date=date.today()
    )

    # 어제 시작됐는데, 오늘 끝난 모임
    meetings_yesterday = MeetingLog.objects.filter(
        meeting__is_deleted=False,
        meeting__end_time=now,
        date=date.today() - timedelta(days=1),
        meeting__start_time__gt=models.F("meeting__end_time"),
    )

    meetings = meetings_today | meetings_yesterday

    # 해당 모임 참여 내역 가져오기
    enter_list = UserMeetingEnter.objects.filter(
        meeting_review_alarm_sent_at=None, meeting__in=meetings
    )

    # 종료/후기 알람톡 보내기
    send_meeting_end_alarm_talk(enter_list)
