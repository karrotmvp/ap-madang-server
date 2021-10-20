from django.contrib import admin
from .models import *
from django import forms
from django.db import models


# @admin.register(Days)
# class DaysAdmin(admin.ModelAdmin):
#     list_display = ("day",)


@admin.register(MeetingLog)
class MeetingLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "meeting",
        "date",
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


@admin.register(UserMeetingEnter)
class UserMeetingEnterAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meeting", "created_at")
