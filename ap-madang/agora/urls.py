from .views import *
from django.urls import path


urlpatterns = [
    path("code", get_meeting_enter_code),
    path("validate-code", get_user_meeting_from_code),
]
