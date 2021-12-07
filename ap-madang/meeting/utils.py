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
        response = s3_client.generate_presigned_post(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key="media/meeting_image/" + file_name,
            ExpiresIn=120,
        )

    except ClientError as e:
        return None

    return response
