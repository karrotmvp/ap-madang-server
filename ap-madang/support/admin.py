from django.contrib import admin
from .models import *
from alarmtalk.views import *
from django.contrib import messages


@admin.register(UserOpinion)
class UserOpinionAdmin(admin.ModelAdmin):
    list_display = ("user", "body", "created_at", "sent_at")

    actions = ["send_open_alarm"]

    def send_open_alarm(self, request, queryset):
        alarm_list = queryset.filter(sent_at=None)
        total_list_num = len(alarm_list)
        total_alarm_num = send_meeting_create_function_alarm_talk_to_opinions(
            alarm_list
        )

        if total_alarm_num != total_list_num:
            messages.add_message(
                request,
                messages.ERROR,
                str(total_list_num)
                + "명 중 "
                + str(total_list_num - total_alarm_num)
                + "명 에게 모임 생성 기능 오픈 알람을 전송하지 못했습니다",
            )

        else:
            messages.add_message(
                request,
                messages.INFO,
                str(total_alarm_num) + "명 에게 모임 생성 기능 오픈 알람을 전송했습니다",
            )

    send_open_alarm.short_description = "모임 생성 기능 오픈 알람 (안 받은 사람) 전체 보내기"


@admin.register(MeetingReview)
class MeetingReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "body", "created_at")
    list_filter = ["meeting__date", "meeting__meeting"]
