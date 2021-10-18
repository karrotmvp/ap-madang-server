from rest_framework import serializers
from .models import *


class UserOpinionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOpinion
        fields = ["user", "body", "created_at"]
