from rest_framework import routers
from .views import *
from django.urls import path

router = routers.DefaultRouter()
router.register(r"", MeetingViewSet)

urlpatterns = router.urls + [
    # path("<int:pk>/enter", UserMeetingEnterViewSet.as_view({"post": "create"})),
    # path("bot", get_meeting_list_for_bot),
]
