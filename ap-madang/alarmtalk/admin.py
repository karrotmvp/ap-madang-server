from django.contrib import admin
from .models import UserMeetingAlarm

# Register your models here.
@admin.register(UserMeetingAlarm)
class UserMeetingAlarmAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meeting", "created_at", "sent_at")
    list_filter = ["meeting__date", "meeting", "sent_at"]
