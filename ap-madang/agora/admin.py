from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(MeetingEnterCode)
class MeetingEnterCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "is_valid", "created_at")
