from django.contrib import admin
from .models import UserMeetingAlarm
from meeting.filters import CustomDateFieldListFilter

# Register your models here.
@admin.register(UserMeetingAlarm)
class UserMeetingAlarmAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meeting", "created_at", "sent_at")
    list_filter = [
        ("meeting__date", CustomDateFieldListFilter),
        "meeting__meeting",
        "sent_at",
    ]
