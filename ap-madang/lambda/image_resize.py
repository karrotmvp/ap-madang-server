import boto3
import uuid
from urllib.parse import unquote_plus
from PIL import Image, ImageOps
import pymysql
import config
import logging
import datetime
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        print("Removed the file %s" % path)
    else:
        print("Sorry, file %s does not exist." % path)


def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail(tuple(x / 2 for x in image.size))
        image.save(resized_path, format="webp")


def update_thumbnail(meeting_id, thumbnail_image_url, env):
    if env == "prod":
        host = config.prod_host
        user = config.prod_username
        password = config.prod_password
        db = config.prod_name
    else:
        host = config.dev_host
        user = config.dev_username
        password = config.dev_password
        db = config.dev_name

    # db setting
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
        )
    except pymysql.MySQLError as e:
        logger.error("Failed to connect to MySQL")
        return {"success": False, "message": "Database Error"}
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    update_sql = "UPDATE meeting_meeting SET updated_at='{}', thumbnail_image_url='{}' WHERE id={};".format(
        datetime.datetime.now(), thumbnail_image_url, meeting_id
    )
    cursor.execute(update_sql)

    conn.commit()
    conn.close()


def lambda_handler(event, context):
    for record in event["Records"]:
        print(record)
        # bucket = record["s3"]["bucket"]["name"]
        # key = unquote_plus(record["s3"]["object"]["key"])

        bucket = record["messageAttributes"]["bucket"]['stringValue']
        key = record["messageAttributes"]["key"]['stringValue']
        meeting_id = record["messageAttributes"]["meeting_id"]['stringValue']
        env = record["messageAttributes"]["env"]['stringValue']

        print(bucket, key, meeting_id)

        # 기존 파일 경로 및 이름"media/meeting_image/" + file_name
        path = key.split("/")[0] + "/" + key.split("/")[1]
        file_name_ext = key.split("/")[-1]
        file_name = file_name_ext.split(".")[0]+"."+file_name_ext.split(".")[1]

        tmpkey = key.replace("/", "")
        download_path = "/tmp/{}{}".format(uuid.uuid4(), tmpkey)
        upload_path = "/tmp/resized-{}".format(tmpkey)

        s3_client.download_file(bucket, key, download_path)
        resize_image(download_path, upload_path)
        thumbnail_file_name = "{}.{}".format(file_name, "webp")
        s3_client.upload_file(
            upload_path,
            config.thumbnail_bucket_name,
            thumbnail_file_name,
            ExtraArgs={"ContentType": "image/webp"},
        )
        delete_file(download_path)
        delete_file(upload_path)

        original_image_url = "meeting_image/" + file_name_ext
        thumbnail_image_url = "https://{}.s3.{}.amazonaws.com/{}".format(
            config.thumbnail_bucket_name, config.bucket_region, thumbnail_file_name
        )
        update_thumbnail(meeting_id, thumbnail_image_url, env)
        logger.info(
            "----- sucessfully uploaded file {} -----".format(
                thumbnail_image_url
            ))

    return {"statusCode": 200, "body": "thumbnail image resize sucess"}
