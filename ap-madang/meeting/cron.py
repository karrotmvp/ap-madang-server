from .models import *
from .utils import *
from sentry_sdk import capture_message


def create_tomorrows_meeting():
    print("----- meeting log creation start : " + str(datetime.now()) + " -----")
    total = 0

    tomorrow = date.today() + timedelta(days=1)
    meetings = Meeting.objects.filter(
        is_deleted=False, days__day=get_date_of_tomorrow()
    )
    meetings_num = meetings.count()

    for meeting in meetings:
        MeetingLog.objects.create(meeting=meeting, date=tomorrow)
        total += 1

    if total != meetings_num:
        capture_message(str(tomorrow) + "의 모임 로그가 생성되지 않았습니다.")
    else:
        print("created " + str(total) + " meeting logs")

    print("----- meeting log creation start : " + str(datetime.now()) + " -----")
    print()
