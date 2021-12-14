from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nickname",
        "manner_temperature",
        "region_name",
        "created_at",
        "sent_at",
    )
