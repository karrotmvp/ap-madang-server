from django.contrib import admin
from .models import *
from django import forms
from django.db import models
from .utils import *
from django.contrib import messages
from django.db.utils import IntegrityError
from .filters import CustomDateFieldListFilter
from alarmtalk.views import send_meeting_end_alarm_talk


@admin.register(Days)
class DaysAdmin(admin.ModelAdmin):
    list_display = ("day",)


@admin.register(MeetingLog)
class MeetingLogAdmin(admin.ModelAdmin):
    readonly_fields = ["meeting"]
    list_display = (
        "id",
        "date",
        "meeting",
        "created_at",
        "alarm_cnt_fake",
        "enter_cnt_fake",
        "alarm_fake_add_cnt",
    )
    list_filter = [("date", CustomDateFieldListFilter),
                   "meeting__region", "meeting"]


def create_meeting_log(request, queryset, date):
    total = 0
    duplicate = 0
    queryset_num = queryset.count()
    meetings = queryset.filter(is_deleted=False, days__day=get_date(date))
    meetings_num = meetings.count()

    for meeting in meetings:
        try:
            MeetingLog.objects.create(meeting=meeting, date=date)
            total += 1
        except IntegrityError:
            duplicate += 1

    if queryset_num != meetings_num:
        base = (
            "선택한 "
            + str(queryset_num)
            + " 개의 모임 중 "
            + str(meetings_num)
            + " 개만이 열려야 하는 모임입니다.(요일 기준) \n "
        )
    else:
        base = ""
    if total != meetings_num:
        messages.add_message(
            request,
            messages.ERROR,
            base
            + str(meetings_num)
            + "개 중 "
            + str(meetings_num - total)
            + "개의 미팅 로그를 생성하지 못했습니다. "
            + str(duplicate)
            + " 개의 미팅 로그가 이미 존재합니다.",
        )
    else:
        messages.add_message(
            request,
            messages.INFO,
            base + str(total) + "개의 미팅 로그를 생성했습니다",
        )


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": forms.CheckboxSelectMultiple}
    }

    list_display = (
        "id",
        "title",
        "region",
        "start_time",
        "end_time",
        "is_deleted",
        "is_video",
    )
    list_filter = ["region", "is_deleted"]
    actions = [
        "create_today_meeting_log",
        "create_tomorrow_meeting_log",
        "duplicate_meeting_to_another_region",
        "create_channel_name",
    ]

    def create_today_meeting_log(self, request, queryset):
        create_meeting_log(request, queryset, date.today())

    def create_tomorrow_meeting_log(self, request, queryset):
        create_meeting_log(request, queryset, date.today() + timedelta(days=1))

    def duplicate_meeting_to_another_region(self, request, queryset):
        total = 0
        meetings = queryset.filter(is_deleted=False)
        for meeting in meetings:
            days = meeting.days.all()
            meeting.pk = None
            meeting.region = "관악구"
            meeting.save()
            meeting.days.set(days)
            total += 1

        messages.add_message(
            request,
            messages.INFO,
            str(total) + "개의 미팅 로그를 생성했습니다",
        )

    def create_channel_name(self, request, queryset):
        total = 0
        meetings = queryset.filter(channel_name__isnull=True)
        for meeting in meetings:
            meeting.channel_name = create_channel_name()
            meeting.save()
            total += 1

        messages.add_message(
            request,
            messages.INFO,
            str(total) + "개의 미팅의 채널 이름을 추가했습니다",
        )

    duplicate_meeting_to_another_region.short_description = "관악구에 동일 모임 생성"
    create_today_meeting_log.short_description = "오늘 미팅 로그 생성"
    create_tomorrow_meeting_log.short_description = "내일 미팅 로그 생성"
    create_channel_name.short_description = "채널 이름이 없는 미팅에, 채널 이름 추가"


@admin.register(UserMeetingEnter)
class UserMeetingEnterAdmin(admin.ModelAdmin):
    readonly_fields = ["meeting", "user"]
    list_display = (
        "id",
        "user",
        "meeting",
        "created_at",
        "meeting_review_alarm_sent_at",
    )
    actions = ["send_review_alarm"]

    def send_review_alarm(self, request, queryset):

        enter_list = queryset.filter(meeting_review_alarm_sent_at=None)
        total_list_num = len(enter_list)

        total_alarm_num = send_meeting_end_alarm_talk(enter_list)

        if total_alarm_num != total_list_num:
            messages.add_message(
                request,
                messages.ERROR,
                str(total_list_num)
                + "명 중 "
                + str(total_list_num - total_alarm_num)
                + "명 에게 모임 후기 알람을 전송하지 못했습니다",
            )

        else:
            messages.add_message(
                request,
                messages.INFO,
                str(total_alarm_num) + "명 에게 모임 후기 알람을 전송했습니다",
            )

    send_review_alarm.short_description = "모임 후기 알림톡 보내기"
