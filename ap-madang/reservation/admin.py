from django.contrib import admin
from .models import Reservation
from alarmtalk.views import send_biz_chat_message
from datetime import datetime


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("nickname", "region", "suggestion", "sent_at", "created_at")
    list_filter = ["sent_at"]
    actions = ["send_open_alarm"]

    def send_open_alarm(self, request, queryset):
        title = "랜선동네모임 서비스가 오픈했어요🎉"
        text = "오픈 알림받기를 신청한 랜선동네모임 서비스를 이제 당근마켓에서 만나볼 수 있어요!\n아래 '서비스 확인하러 가기' 버튼을 눌러 이웃을 만나보세요."
        primary_button_text = "서비스 확인하러 가기"
        primary_button_url = "https://www.daangn.com"
        total_alarm_num = 0

        alarm_list = queryset.filter(sent_at=None)
        print("----- user meeting alarm start : " + str(datetime.now()) + " -----")
        for alarm in alarm_list:
            if send_biz_chat_message(
                alarm.userid,
                title,
                text,
                primary_button_url,
                primary_button_text,
            ):
                print("Alarm sent! to ", alarm.userid)
                alarm.sent_at = datetime.now()
                alarm.save()
                total_alarm_num += 1

            else:
                # TODO 우리한테 노티스 보내기? 아니면 retry 하기?
                pass

        print(
            "----- user service open alarm end with : "
            + str(datetime.now())
            + " alarm talks total ",
            total_alarm_num,
            "-----",
        )

    send_open_alarm.short_description = "오픈 알람 (안 받은 사람) 전체 보내기"
