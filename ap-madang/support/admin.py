from django.contrib import admin
from .models import *


@admin.register(UserOpinion)
class UserOpinionAdmin(admin.ModelAdmin):
    list_display = ("user", "body", "created_at")
