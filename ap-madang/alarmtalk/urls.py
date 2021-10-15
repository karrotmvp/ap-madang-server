from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r"meetings", UserMeetingAlarmViewSet)

urlpatterns = router.urls + []
