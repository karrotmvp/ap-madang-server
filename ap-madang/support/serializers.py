from rest_framework import serializers
from .models import *


class UserOpinionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOpinion
        fields = ["user", "body", "created_at"]


class MeetingReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingReview
        fields = ["user", "meeting", "body", "created_at"]
