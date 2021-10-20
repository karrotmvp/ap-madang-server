from django.contrib import admin
from .models import *
from django import forms
from django.db import models
from .utils import *
from django.contrib import messages


@admin.register(Days)
class DaysAdmin(admin.ModelAdmin):
    list_display = ("day",)


@admin.register(MeetingLog)
class MeetingLogAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "meeting", "created_at")
    list_filter = ["date", "meeting"]


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
    actions = ["create_today_meeting_log"]

    def create_today_meeting_log(self, request, queryset):
        total = 0
        meetings = queryset.filter(is_deleted=False, days__day=get_date_of_today())
        meetings_num = meetings.count()

        for meeting in meetings:
            MeetingLog.objects.create(meeting=meeting, date=date.today())
            total += 1

        if total != meetings_num:
            messages.add_message(
                request,
                messages.ERROR,
                str(total)
                + "개 중 "
                + str(total - meetings_num)
                + "개의 미팅 로그를 생성하지 못했습니다",
            )
        else:
            messages.add_message(
                request,
                messages.INFO,
                str(total) + "개의 미팅 로그를 생성했습니다",
            )

    create_today_meeting_log.short_description = "오늘 미팅 로그 생성"


@admin.register(UserMeetingEnter)
class UserMeetingEnterAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meeting", "created_at")
