from django.contrib import admin
from .models import *


@admin.register(UserOpinion)
class UserOpinionAdmin(admin.ModelAdmin):
    list_display = ("user", "body", "created_at")


@admin.register(MeetingReview)
class MeetingReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "body", "created_at")
    list_filter = ["meeting__date", "meeting"]
