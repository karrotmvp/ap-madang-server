from django.contrib import admin
from .models import Reservation
from alarmtalk.views import send_biz_chat_message
from datetime import datetime
from django.contrib import messages
from sentry_sdk import capture_message
from config.settings import CLIENT_BASE_URL


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("nickname", "region", "suggestion", "sent_at", "created_at")
    list_filter = ["sent_at"]
    actions = ["send_open_alarm"]

    def send_open_alarm(self, request, queryset):
        title = "랜선동네모임 서비스가 오픈했어요🎉"
        text = "오픈 알림받기를 신청한 랜선동네모임 서비스를 이제 당근마켓에서 만나볼 수 있어요!\n지금 바로 랜동모에서 열리는 모임을 구경하고, 관심 있는 모임에 참여해 보세요."
        primary_button_text = "모임 둘러보러 가기"
        primary_button_url = "karrot://minikarrot/router?app=https%3A%2F%2Fwebview.prod.kr.karrotmarket.com%2Fwidget-profile&path=%2Fprofiles%2FV2lkZ2V0OjYxNjdhMjY3MTRjYmRjZjZiNTcwMjU3Ng%3D%3D&navbar=false&scrollable=false"
        total_alarm_num = 0

        alarm_list = queryset.filter(sent_at=None)
        total_list_num = len(alarm_list)
        for alarm in alarm_list:
            if send_biz_chat_message(
                alarm.userid,
                title,
                text,
                primary_button_url,
                primary_button_text,
                False,
            ):
                print(
                    "Alarm sent! to nickname:{}, karrot_id : {}".format(
                        alarm.nickname, alarm.userid
                    )
                )
                alarm.sent_at = datetime.now()
                alarm.save()
                total_alarm_num += 1

            else:
                capture_message(
                    "서비스 오픈 알림톡이 전송되지 않았습니다. reservation.id = " + str(alarm.id)
                )
                pass

        if total_alarm_num != total_list_num:
            messages.add_message(
                request,
                messages.ERROR,
                str(total_list_num)
                + "명 중 "
                + str(total_list_num - total_alarm_num)
                + "명 에게 오픈 알람을 전송하지 못했습니다",
            )

        else:
            messages.add_message(
                request,
                messages.INFO,
                str(total_alarm_num) + "명 에게 오픈 알람을 전송했습니다",
            )

    send_open_alarm.short_description = "오픈 알람 (안 받은 사람) 전체 보내기"
