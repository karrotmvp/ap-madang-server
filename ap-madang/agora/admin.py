from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(MeetingEnterCode)
class MeetingEnterCodeAdmin(admin.ModelAdmin):
    readonly_fields = ["meeting", "user"]
    list_display = ("user", "meeting", "is_valid", "created_at")
