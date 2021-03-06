import jwt, json, requests, random, string
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

    payload = json.dumps(
        {
            "topic": meeting.meeting.title,
            "type": "2",
            "start_time": meeting.date
            + "T"
            + meeting.meeting.start_time.strftime("%H:%M:%S"),
            "duration": str(duration),
            "timezone": "Asia/Seoul",
            "password": "".join(
                random.choices(
                    string.ascii_letters + string.digits,
                    k=5,
                )
            ),
            "settings": {
                "host_video": "false",
                "participant_video": "false",
                "join_before_host": "true",
                "waiting_room": "false",
                "meeting_authentication": "false",
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


def delete_zoom_meeting(meeting_url):
    zoom_meeting_id = meeting_url[18 : meeting_url.find("?")]
    url = "https://api.zoom.us/v2/meetings/" + zoom_meeting_id

    payload = {}
    headers = {
        "Authorization": "Bearer " + generate_jwt_for_zoom(),
        "User-Agent": "Zoom-Jwt-Request",
        "Content-Type": "application/json",
    }

    response = requests.request("DELETE", url, headers=headers, data=payload)

    return response.status_code == 204
