from django.contrib import admin
from .models import Meeting, UserMeetingEnter

# Register your models here.
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "region", "start_time", "end_time", "is_deleted")


@admin.register(UserMeetingEnter)
class UserMeetingEnterAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "meeting", "created_at")
