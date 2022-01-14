from datetime import date, timedelta, datetime

from meeting.models import MeetingLog
from meeting.utils import get_live_status
from .views import get_agora_channel_user_list


def update_agora_user_list():
    # 지금 열리는 모임 가져오기
    today = date.today()
    meetings = MeetingLog.objects.filter(
        meeting__is_deleted=False,
        date__range=(today - timedelta(days=1), today),
        meeting__is_video=False,
    ).prefetch_related("meeting")
    filtered_meetings = []

    for meeting in meetings:
        live_status = get_live_status(
            meeting.date,
            meeting.meeting.start_time,
            meeting.meeting.end_time,
        )
        if live_status == "live":
            filtered_meetings.append(meeting)

    # 개수가 20개가 넘어간다면, 현재 시간의 "초"가 홀수라면 홀수 아이디, 짝수라면 짝수 아이디를 가진 모임만 업데이트한다
    if 20 < len(filtered_meetings):
        now = datetime.now().second
        left = now % 2
        filtered_meetings = [
            meeting for meeting in filtered_meetings if meeting.id / 2 == left
        ]

    # 모임 유저 리스트 업데이트하기
    for meeting in filtered_meetings:
        response_data = get_agora_channel_user_list(meeting.meeting.channel_name).get(
            "data"
        )
        channel_exist = response_data.get("channel_exist")

        # 채널이 존재하면(사람이 있으면) 유저 리스트를 받아와서 업데이트 해준다
        if channel_exist:
            users = response_data.get("users")
            meeting.agora_user_list = users
        else:
            # 채널이 존재하지 않으면, 아무도 없다는 뜻이므로 리스트를 비워준다
            meeting.agora_user_list = "[]"
        meeting.save()

    print(
        "----- meeting agora_user_list update with total :{} , time: {}-----".format(
            len(filtered_meetings), str(datetime.now())
        )
    )
