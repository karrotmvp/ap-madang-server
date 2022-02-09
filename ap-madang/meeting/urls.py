from rest_framework import routers
from .views import *
from django.urls import path

router = routers.DefaultRouter()
router.register(r"", MeetingViewSet)

urlpatterns = router.urls + [
    path("<int:pk>/enter", UserMeetingEnterViewSet.as_view({"post": "create"})),
    path("<int:pk>/close", close_meeting),
    path("presigned-url", get_presigned_url),
    path("<int:pk>/user-list", get_meeting_agora_user_list),
    path("link", create_meeting_link),
    path("link/<int:pk>/close", close_meeting_link),
]
