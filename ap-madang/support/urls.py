from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r"opinion", UserOpinionViewSet)
router.register(r"meeting-review", MeetingReviewViewSet)

urlpatterns = router.urls + []
