import json
import pymysql
import config
import datetime
import karrot_api
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # db setting
    try:
        conn = pymysql.connect(
            host=config.host,
            user=config.username,
            password=config.password,
            db=config.name,
        )
    except pymysql.MySQLError as e:
        logger.error("Failed to connect to MySQL")
        return {"success": False, "message": "Database Error"}
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    title = "지금 모임이 시작됐어요 🙌"
    text = "알림 신청하신 [ {} ] 모임이 시작됐어요.\n아래 '모임 바로가기' 버튼을 눌러 이웃과 대화를 나눠보세요."
    primary_button_text = "모임 바로가기"
    normal_button_url = "{}/index.html?#/".format(config.dev_client_base_url)
    normal_button_text = "랜동모 홈으로 가기"
    total_alarm_num = 0
    fail_alarm_num = 0

    now = datetime.datetime.now().strftime("%H:%M:00")
    today = datetime.date.today().strftime("%Y-%m-%d")

    sql = """
        SELECT
            a.id, a.user_id, a.meeting_id, a.sent_at, u.karrot_user_id, m.title
        FROM
            alarmtalk_usermeetingalarm as a
        LEFT JOIN user_user as u ON a.user_id=u.id
        LEFT JOIN meeting_meetinglog as ml ON a.meeting_id=ml.id
        LEFT JOIN meeting_meeting as m ON m.id=ml.meeting_id
        WHERE
        (
            a.meeting_id IN (
            SELECT
                U0.`id`
            FROM
                `meeting_meetinglog` U0
                INNER JOIN `meeting_meeting` U1 ON (U0.`meeting_id` = U1.`id`)
            WHERE
                (
                U0.date = '{}'
                AND NOT U1.is_deleted
                AND U1.start_time = '{}'
                )
            )
            AND a.sent_at IS NULL
        );
    """.format(
        today, now
    )

    cursor.execute(sql)
    data = cursor.fetchall()
    logger.info(
        "----- user meeting alarm start : {} -----".format(str(datetime.datetime.now()))
    )

    for alarm in data:
        url = "{}/index.html?#/meetings/{}".format(
            config.dev_client_base_url,
            str(alarm["meeting_id"]),
        )
        if karrot_api.send_biz_chat_message(
            alarm["karrot_user_id"],
            title,
            text.format(alarm["title"]),
            url,
            primary_button_text,
            True,
            normal_button_url,
            normal_button_text,
        ):
            update_sql = "UPDATE alarmtalk_usermeetingalarm SET updated_at='{}', sent_at='{}' WHERE id={}".format(
                datetime.datetime.now(), datetime.datetime.now(), alarm["id"]
            )
            cursor.execute(update_sql)
            logger.info(
                "SUCCESS: Alarm sent! id = {}, karrot_id: {}".format(
                    alarm["id"], alarm["karrot_user_id"]
                )
            )
            total_alarm_num += 1

        else:
            fail_alarm_num += 1
            error_msg = (
                "ERROR : 모임 시작 알림톡이 전송되지 않았습니다. usermeetingalarm.id = {}".format(
                    alarm["id"]
                )
            )
            logger.error(error_msg)
            requests.post(
                config.slack_url,
                data=json.dumps({"text": error_msg}),
                headers={"Content-Type": "application/json"},
            )

    conn.commit()
    conn.close()

    logger.info(
        "----- {} user meeting alarm end with : {} alarm talks total -----".format(
            str(datetime.datetime.now()), str(total_alarm_num)
        )
    )
    if data:
        payloads = {
            "text": "{}시에 {} 명에게 알람톡을 전송했습니다. {} 명에게 알람톡을 보내지 못했습니다.".format(
                now, str(total_alarm_num), str(fail_alarm_num)
            )
        }
        requests.post(
            config.slack_url,
            data=json.dumps(payloads),
            headers={"Content-Type": "application/json"},
        )

    return {"statusCode": 200, "body": "success"}


# lambda_handler(None, None)
