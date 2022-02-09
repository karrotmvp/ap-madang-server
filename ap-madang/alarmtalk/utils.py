from config.settings import CLIENT_BASE_URL, ERROR_SLACK_WEBHOOK_URL
from common.utils import get_env_name
import json, requests


def time_to_korean(time, twelve_base=False):
    hour = time.strftime("%-H")

    if twelve_base:
        if int(hour) > 12:
            hour = "오후 " + str(int(hour) - 12)
        else:
            hour = "오전 " + hour

    korean = "{}시".format(hour)
    min = time.strftime("%-M")
    if min != "0":
        korean += " {}분".format(min)
    return korean


def date_and_time_to_korean(date, time):

    return "{}년 {}월 {}일 {}".format(
        date.strftime("%Y"),
        date.strftime("%-m"),
        date.strftime("%-d"),
        time_to_korean(time),
    )


def get_meeting_detail_client_page(meeting_id):
    return "{}/index.html?#/meetings/{}?ref=alarm".format(
        CLIENT_BASE_URL, str(meeting_id)
    )


def get_home_client_page():
    return "{}/index.html?#/".format(
        CLIENT_BASE_URL,
    )


def get_meeting_title_trunc(meeting_title):
    MAX_LENGTH = 15
    if len(meeting_title) > MAX_LENGTH:
        return meeting_title[0:MAX_LENGTH] + "..."
    return meeting_title


def send_alarmtalk_error_slack_webhook(text):
    if get_env_name() != "prod":
        return None

    payloads = {"text": text}
    res = requests.post(
        ERROR_SLACK_WEBHOOK_URL,
        data=json.dumps(payloads),
        headers={"Content-Type": "application/json"},
    )
