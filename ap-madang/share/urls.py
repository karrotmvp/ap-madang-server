from rest_framework import routers
from .views import *
from django.urls import path

urlpatterns = [
    path("short-url/meeting", get_or_create_short_url),
    path("redirect", redirect_to_karrot_scheme),
]
