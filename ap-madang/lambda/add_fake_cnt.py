import pymysql
import config
import datetime
import logging
import random

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_live_status(meeting):
    now = datetime.datetime.now().time()
    start = meeting["start_time"].time()
    end = meeting["end_time"].time()
    if meeting["date"] != datetime.date.today():
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

    now = datetime.datetime.now().strftime("%H:%M:00")
    today = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    sql = """
        SELECT 
            ml.id, 
            ml.meeting_id, 
            ml.date, 
            m.start_time, 
            m.end_time
        FROM 
            meeting_meetinglog as ml
        INNER JOIN meeting_meeting as m ON ml.meeting_id = m.id 
        WHERE 
            (
                ml.date IN ('{}', '{}') 
                AND NOT m.is_deleted
            );
    """.format(
        today, tomorrow
    )

    cursor.execute(sql)
    data = cursor.fetchall()
    logger.info(
        "----- meeting log creation start : " + str(datetime.datetime.now()) + " -----"
    )
    print(data)

    for meeting in data:
        live_status = get_live_status(meeting)
        print(live_status)
        # if live_status == 0:
        #     meeting.enter_cnt_fake += get_enter_increment()
        # elif live_status == 1 and meeting.alarm_fake_add_cnt < 100:
        #     meeting.alarm_cnt_fake += get_alarm_increment()
        #     meeting.alarm_fake_add_cnt += 1
        # meeting.save()

    #     update_sql = "UPDATE alarmtalk_usermeetingalarm SET updated_at='{}', sent_at='{}' WHERE id={}".format(
    #         datetime.datetime.now(), datetime.datetime.now(), alarm["id"]
    #     )
    #     cursor.execute(update_sql)
    #     logger.info(
    #         "SUCCESS: Alarm sent! id = {}, karrot_id: {}".format(
    #             alarm["id"], alarm["karrot_user_id"]
    #         )
    #     )
    #     total_alarm_num += 1

    #     else:
    #         fail_alarm_num += 1
    #         error_msg = (
    #             "ERROR : 모임 시작 알림톡이 전송되지 않았습니다. usermeetingalarm.id = {}".format(
    #                 alarm["id"]
    #             )
    #         )
    #         logger.error(error_msg)
    #         requests.post(
    #             config.slack_url,
    #             data=json.dumps({"text": error_msg}),
    #             headers={"Content-Type": "application/json"},
    #         )

    # conn.commit()
    # conn.close()

    # logger.info(
    #     "----- {} user meeting alarm end with : {} alarm talks total -----".format(
    #         str(datetime.datetime.now()), str(total_alarm_num)
    #     )
    # )
    # if data:
    #     payloads = {
    #         "text": "{}시에 {} 명에게 알람톡을 전송했습니다. {} 명에게 알람톡을 보내지 못했습니다.".format(
    #             now, str(total_alarm_num), str(fail_alarm_num)
    #         )
    #     }
    #     requests.post(
    #         config.slack_url,
    #         data=json.dumps(payloads),
    #         headers={"Content-Type": "application/json"},
    #     )

    return {"statusCode": 200, "body": "success"}


lambda_handler(None, None)
