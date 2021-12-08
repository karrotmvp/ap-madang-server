from datetime import date, timedelta, datetime
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME,
)
import boto3
from botocore.exceptions import ClientError
from uuid import uuid4
import mimetypes
from urllib.parse import urlparse
import random

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
    file_name = "{}{}{}".format(datetime.now(), uuid4().hex, file_name)

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

    except ClientError as e:
        return None

    return response


def get_live_status(start_date, start_time, end_time):
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
