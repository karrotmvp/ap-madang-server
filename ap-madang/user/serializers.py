from rest_framework import serializers
from .models import *


DEFAULT_PROFILE_IMAGE_URL = {
    0: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default1.png",
    1: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default2.png",
    2: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default3.png",
    3: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/default_profile_image/default4.png",
}


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
        return (
            obj.profile_image_url
            if obj.profile_image_url
            else DEFAULT_PROFILE_IMAGE_URL.get(obj.id % 4)
        )
