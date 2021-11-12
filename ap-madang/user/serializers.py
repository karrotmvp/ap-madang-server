from rest_framework import serializers
from .models import *


DEFAULT_PROFILE_IMAGE_URL = {
    0: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/media/meeting_image/2021-10-19_180218.1465851.jpg",
    1: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/media/meeting_image/2021-10-19_180218.1465851.jpg",
    2: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/media/meeting_image/2021-10-19_180218.1465851.jpg",
    3: "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/media/meeting_image/2021-10-19_180218.1465851.jpg",
}


class UserSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "nickname", "profile_image_url", "manner_point"]

    def get_profile_image_url(self, obj):
        return (
            obj.profile_image_url
            if obj.profile_image_url
            else DEFAULT_PROFILE_IMAGE_URL.get(obj.id % 4)
        )
