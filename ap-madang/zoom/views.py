import jwt, json, requests
from datetime import datetime, timedelta

from config.settings import ZOOM_API_KEY, ZOOM_API_SECRET


def generate_jwt_for_zoom():
    token = jwt.encode(
        {
            "iss": ZOOM_API_KEY,
            "exp": (datetime.now() + timedelta(minutes=90)).timestamp(),
        },
        ZOOM_API_SECRET,
        algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT"},
    )
    return token


def create_zoom_meeting(meeting):
    url = "https://api.zoom.us/v2/users/me/meetings"

    start_time = meeting.meeting.start_time
    end_time = meeting.meeting.end_time
    date = datetime.strptime(meeting.date, "%Y-%m-%d").date()
    start_datetime = datetime.combine(date, start_time)
    if start_time > end_time:
        end_datetime = datetime.combine(date + timedelta(days=1), end_time)
    else:
        end_datetime = datetime.combine(date, end_time)

    duration = int((end_datetime - start_datetime).seconds / 60)

    print(duration)

    payload = json.dumps(
        {
            "topic": meeting.meeting.title,
            "type": "2",
            "start_time": meeting.date
            + "T"
            + meeting.meeting.start_time.strftime("%H:%M:%S"),
            "duration": str(duration),
            "timezone": "Asia/Seoul",
            "settings": {
                "host_video": "false",
                "participant_video": "false",
                "join_before_host": "true",
            },
        }
    )
    headers = {
        "Authorization": "Bearer " + generate_jwt_for_zoom(),
        "User-Agent": "Zoom-Jwt-Request",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text).get("join_url")
