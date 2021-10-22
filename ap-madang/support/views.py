from rest_framework import viewsets, mixins
from user.jwt_authentication import jwt_authentication
from .models import *
from .serializers import *


class UserOpinionViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserOpinionSerializer
    queryset = UserOpinion.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().create(request, *args, **kwargs)


class MeetingReviewViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MeetingReviewSerializer
    queryset = MeetingReview.objects.all()

    @jwt_authentication
    def create(self, request, *args, **kwargs):
        self.request.data.update({"user": request.user.id, "region": request.region})
        return super().create(request, *args, **kwargs)
