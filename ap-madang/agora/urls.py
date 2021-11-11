from .views import *
from django.urls import path


urlpatterns = [
    path("validate-code", get_user_meeting_from_code),
]
