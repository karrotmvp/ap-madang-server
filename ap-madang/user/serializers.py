from rest_framework import serializers
from .models import *
from .utils import *


class UserSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_image_url",
            "manner_temperature",
            "region_name",
        ]

    def get_profile_image_url(self, obj):
        return get_profile_image_url(obj)
