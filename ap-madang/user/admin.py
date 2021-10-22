from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "karrot_user_id", "manner_point")
    list_filter = ["nickname"]
