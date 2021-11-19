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
            MeetingLog.objects.create(meeting=meeting, date=day_aft_tom)
            total += 1
        except IntegrityError:
            duplicate += 1

    if total != meetings_num:
        capture_message(
            "{}의 모임 {}개 중 {}개의 미팅 로그를 생성하지 못했습니다. {}개의 미팅 로그가 이미 존재합니다.".format(
                str(day_aft_tom),
                str(meetings_num),
                str(meetings_num - total),
                str(duplicate),
            ),
            "error",
        )
    else:
        print("created " + str(total) + " meeting logs")

    print("----- meeting log creation end : " + str(datetime.now()) + " -----")
    print()


def get_live_status(meeting):
    now = datetime.now().time()
    start = meeting.meeting.start_time
    end = meeting.meeting.end_time
    if meeting.date != date.today():
        return 1  # tomorrow
    if (start <= now < end) or (start > end and (now >= start or now < end)):
        return 0  # live
    if now < start:
        return 1  # upcoming
    return 2  # finish


def get_alarm_increment():
    return random.choice([0, 0, 0, 1, 1])


def get_enter_increment():
    return random.choice([0, 0, 0, 1, 1, 1, 1, 1, 2, 2])


def add_fake_cnt():
    print("----- add fake count" + str(datetime.now()) + " -----")
    meetings = MeetingLog.objects.filter(
        meeting__is_deleted=False,
        date__in=[date.today(), date.today() + timedelta(days=1)],
    ).select_related("meeting")
    for meeting in meetings:
        live_status = get_live_status(meeting)
        if live_status == 0:
            meeting.enter_cnt_fake += get_enter_increment()
        elif live_status == 1 and meeting.alarm_fake_add_cnt < 100:
            meeting.alarm_cnt_fake += get_alarm_increment()
            meeting.alarm_fake_add_cnt += 1
        meeting.save()
