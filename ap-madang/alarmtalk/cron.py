from meeting.models import UserMeetingEnter
from .models import *
from .views import *
from datetime import date, timedelta
from django.db.models import F


def send_meeting_alarm():
    total_alarm_num = 0
    print(
        "----- meeting related alarm talk send start : "
        + str(datetime.now())
        + " -----"
    )

    now = datetime.strftime(datetime.now(), "%H:%M:%000")

    # 현재 시간에 열리는 모임 리스트 가져오기
    meetings = MeetingLog.objects.prefetch_related("meeting", "meeting__user").filter(
        meeting__is_deleted=False, meeting__start_time=now, date=date.today()
    )

    # 해당 모임 예약 내역 가져오기
    alarm_list = UserMeetingAlarm.objects.prefetch_related(
        "user", "meeting", "meeting__meeting"
    ).filter(sent_at=None, meeting__in=meetings)

    # 오픈 알람톡 보내기
    total_alarm_num += send_meeting_start_alarm_talk_to_owners(meetings)
    total_alarm_num += send_meeting_start_alarm_talk(alarm_list)

    # 현재 시간에 끝나는 모임 리스트 가져오기
    meetings_today = MeetingLog.objects.filter(
        meeting__is_deleted=False,
        meeting__end_time=now,
        date=date.today(),
        meeting__start_time__lt=models.F("meeting__end_time"),
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
    enter_list = UserMeetingEnter.objects.prefetch_related(
        "user", "meeting", "meeting__meeting"
    ).filter(meeting_review_alarm_sent_at=None, meeting__in=meetings)

    # 종료/후기 알람톡 보내기
    total_alarm_num += send_meeting_end_alarm_talk(enter_list)

    after_one_hour_date = (datetime.now() + timedelta(hours=1)).date()
    after_one_hour_time = datetime.strftime(
        datetime.now() + timedelta(hours=1), "%H:%M:%000"
    )

    # 한시간 뒤에 열리는 모임 리스트 가져오기
    meetings = MeetingLog.objects.prefetch_related("meeting", "meeting__user").filter(
        meeting__is_deleted=False,
        meeting__start_time=after_one_hour_time,
        date=after_one_hour_date,
    )
    # 해당 모임 예약 내역 가져오기
    alarm_list = UserMeetingAlarm.objects.prefetch_related(
        "user", "meeting", "meeting__meeting"
    ).filter(sent_at=None, meeting__in=meetings)

    # 한 시간 뒤 오픈 알람톡 보내기
    total_alarm_num += send_meeting_start_in_hour_alarm_talk_to_owners(meetings)
    total_alarm_num += send_meeting_start_in_hour_alarm_talk(alarm_list)

    print(
        "----- meeting related alarm talk send end : "
        + str(datetime.now())
        + "with alarm talks total ",
        total_alarm_num,
        "-----",
    )
