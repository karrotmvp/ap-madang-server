from django.contrib import admin
from .models import *
from django import forms
from django.db import models
from .utils import *
from django.contrib import messages
from django.db.utils import IntegrityError


@admin.register(Days)
class DaysAdmin(admin.ModelAdmin):
    list_display = ("day",)


@admin.register(MeetingLog)
class MeetingLogAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "meeting", "created_at")
    list_filter = ["date", "meeting"]


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
    )
    list_filter = ["title", "region", "is_deleted"]
    actions = [
        "create_today_meeting_log",
        "create_tomorrow_meeting_log",
        "duplicate_meeting_to_another_region",
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

    duplicate_meeting_to_another_region.short_description = "관악구에 동일 모임 생성"
    create_today_meeting_log.short_description = "오늘 미팅 로그 생성"
    create_tomorrow_meeting_log.short_description = "내일 미팅 로그 생성"


@admin.register(UserMeetingEnter)
class UserMeetingEnterAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meeting", "created_at")
