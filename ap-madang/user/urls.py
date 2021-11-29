from django.urls import path
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register(r"", UserViewSet)

urlpatterns = router.urls + [
    path("login", login),
    path("me/meetings", UserMeetingViewSet.as_view({"get": "list"})),
]
