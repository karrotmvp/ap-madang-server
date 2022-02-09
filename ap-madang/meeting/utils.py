from datetime import date, timedelta, datetime
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME,
    MEETING_CREATE_SLACK_WEBHOOK_URL,
    ENV_NAME,
    IMAGE_RESIZE_SQS_URL,
    MEETING_ENTER_SLACK_WEBHOOK_URL,
)
from botocore.exceptions import ClientError
from uuid import uuid4
from urllib.parse import urlparse
import random
import requests
import json
import mimetypes
import boto3
from alarmtalk.utils import date_and_time_to_korean
from sentry_sdk import capture_message
from common.utils import get_env_name

DAY_TO_MODEL = {
    0: "0_MON",
    1: "1_TUE",
    2: "2_WED",
    3: "3_THUR",
    4: "4_FRI",
    5: "5_SAT",
    6: "6_SUN",
}


def get_date_of_today():
    return DAY_TO_MODEL.get(date.today().weekday(), None)


def get_date_of_tomorrow():
    tommorow = date.today() + timedelta(days=1)
    return DAY_TO_MODEL.get(tommorow.weekday(), None)


def get_date(date):
    return DAY_TO_MODEL.get(date.weekday(), None)


def generate_presigned_url(file_name):
    file_name = "{}{}.{}".format(datetime.now(), uuid4().hex, file_name.split(".")[-1])
    file_name = file_name.replace(" ", "")

    s3_client = boto3.client(
        "s3",
        region_name=AWS_S3_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    try:
        type = mimetypes.guess_type(file_name)[0]
        response = s3_client.generate_presigned_post(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key="media/meeting_image/" + file_name,
            Fields={"Content-Type": type},
            Conditions=[{"Content-Type": type}],
            ExpiresIn=120,
        )
        # response = s3_client.generate_presigned_url(
        #     ClientMethod="put_object",
        #     Params={
        #         "Bucket": AWS_STORAGE_BUCKET_NAME,
        #         "Key": "media/meeting_image/" + file_name,
        #         # "ContentType": type,
        #         # "ACL": "public-read",
        #     },
        #     ExpiresIn=100,
        # )

    except ClientError as e:
        return None

    return response


def get_live_status(start_date, start_time, end_time):
    if start_date == start_time == end_time == None:
        return None
    now = datetime.now().time()
    start = start_time
    end = end_time
    meeting_start_date = start_date
    today_date = date.today()
    tomorrow_date = date.today() + timedelta(days=1)
    # 내일 시작되는 모임
    if meeting_start_date == tomorrow_date:
        return "tomorrow"
    # 내일 이후 ~ 7일 이내 시작되는 모임
    if meeting_start_date > tomorrow_date:
        return "upcoming"
    # 현재 진행중인 모임
    if (meeting_start_date == today_date and start <= now < end) or (
        start > end
        and (
            (meeting_start_date == today_date and now >= start)
            or (meeting_start_date == today_date - timedelta(days=1) and now < end)
        )
    ):
        return "live"
    # 오늘 예정된 모임
    if meeting_start_date == today_date and now < start:
        return "today"
    # 이미 종료된 모임
    return "finish"


DEFAULT_MEETING_IMAGE = {
    0: "default_meeting_image01.webp",
    1: "default_meeting_image02.webp",
    2: "default_meeting_image03.webp",
    3: "default_meeting_image04.webp",
    4: "default_meeting_image05.webp",
    5: "default_meeting_image06.webp",
}


def get_meeting_image(image_url):
    if image_url is None:
        return (
            "meeting_image/"
            + DEFAULT_MEETING_IMAGE[random.choice(range(len(DEFAULT_MEETING_IMAGE)))]
        )
    return "meeting_image/" + urlparse(image_url).path.split("/")[-1]


def send_meeting_create_slack_webhook(meeting_log):
    if get_env_name() != "prod":
        return None

    datetime_in_korean = date_and_time_to_korean(
        datetime.strptime(meeting_log.date, "%Y-%m-%d").date(),
        meeting_log.meeting.start_time,
    )

    payloads = {
        "text": "환경 : {} \nJinny 주인님🙇‍♂️, [ {} ] 님이 [ {} ]에 [ {} ] 모임을 생성했습니다!! \n모임 시작 일시 : {}".format(
            ENV_NAME,
            meeting_log.meeting.user.nickname,
            meeting_log.meeting.region,
            meeting_log.meeting.title,
            datetime_in_korean,
        )
    }
    res = requests.post(
        MEETING_CREATE_SLACK_WEBHOOK_URL,
        data=json.dumps(payloads),
        headers={"Content-Type": "application/json"},
    )


def send_meeting_link_create_slack_webhook(meeting_log):
    if get_env_name() != "prod":
        return None

    payloads = {
        "text": "환경 : {} \nJinny 주인님🙇‍♂️, [ {} ] 님이 모임 링크를 생성했습니다! id = {}".format(
            ENV_NAME, meeting_log.meeting.user.nickname, str(meeting_log.id)
        )
    }
    res = requests.post(
        MEETING_CREATE_SLACK_WEBHOOK_URL,
        data=json.dumps(payloads),
        headers={"Content-Type": "application/json"},
    )


def send_image_resize_sqs_msg(meeting_id, image_url):
    sqs_client = boto3.client("sqs", region_name=AWS_S3_REGION_NAME)
    try:
        msg = sqs_client.send_message(
            QueueUrl=IMAGE_RESIZE_SQS_URL,
            MessageBody=image_url,
            MessageAttributes={
                "meeting_id": {"StringValue": str(meeting_id), "DataType": "String"},
                "bucket": {"StringValue": "ap-madang-server", "DataType": "String"},
                "env": {"StringValue": get_env_name(), "DataType": "String"},
                "key": {
                    "StringValue": image_url.split("com/")[1],
                    "DataType": "String",
                },
            },
        )
    except ClientError as e:
        capture_message("썸네일 이미지가 생성되지 않았습니다")
        return None
    return msg


def send_meeting_enter_slack_webhook(user, meeting_log):
    if get_env_name() != "prod":
        return None

    payloads = {
        "text": "멍! [ {} ] 님이 모임에 입장했멍! ( meetinglog_id = {}, user_id = {} )".format(
            user.nickname, str(meeting_log.id), str(user.id)
        )
    }
    res = requests.post(
        MEETING_ENTER_SLACK_WEBHOOK_URL,
        data=json.dumps(payloads),
        headers={"Content-Type": "application/json"},
    )


def set_start_end_time(start_time):
    if start_time:
        end_time = datetime.strptime(start_time, "%H:%M:%S") + timedelta(hours=3)
        return start_time, end_time.time()

    now = datetime.now()
    three_hours_later = now + timedelta(hours=3)
    return now.time(), three_hours_later.time()
