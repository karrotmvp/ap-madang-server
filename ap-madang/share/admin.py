from django.contrib import admin
from .models import ShareUrl


@admin.register(ShareUrl)
class ShareUrlAdmin(admin.ModelAdmin):
    list_display = ("id", "origin_url", "code", "access_cnt")
