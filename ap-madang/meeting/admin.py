from django.contrib import admin
from .models import Meeting, UserMeetingEnter

# Register your models here.
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "start_time", "end_time")


@admin.register(UserMeetingEnter)
class UserMeetingEnterAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "created_at")
