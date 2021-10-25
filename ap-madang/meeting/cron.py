from .models import *
from .utils import *
from sentry_sdk import capture_message
from django.db.utils import IntegrityError


def create_tomorrows_meeting():
    print("----- meeting log creation start : " + str(datetime.now()) + " -----")
    total = 0
    duplicate = 0

    day_aft_tom = date.today() + timedelta(days=2)
    meetings = Meeting.objects.filter(is_deleted=False, days__day=get_date(day_aft_tom))
    meetings_num = meetings.count()

    for meeting in meetings:
        try:
            MeetingLog.objects.create(meeting=meeting, date=date)
            total += 1
        except IntegrityError:
            duplicate += 1

    if total != meetings_num:
        capture_message(
            str(day_aft_tom)
            + "의 모임"
            + str(meetings_num)
            + "개 중 "
            + str(meetings_num - total)
            + "개의 미팅 로그를 생성하지 못했습니다. "
            + str(duplicate)
            + " 개의 미팅 로그가 이미 존재합니다."
        )
    else:
        print("created " + str(total) + " meeting logs")

    print("----- meeting log creation end : " + str(datetime.now()) + " -----")
    print()
