from rest_framework import serializers
from agora.models import MeetingEnterCode
from user.serializers import UserSerializer
from meeting.models import MeetingLog
import json


class MeetingLogSimpleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    channel_name = serializers.SerializerMethodField()
    sub_topics = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = MeetingLog
        fields = [
            "id",
            "title",
            "channel_name",
            "sub_topics",
            "description",
            "host",
            "date",
            "start_time",
            "end_time",
        ]

    def get_title(self, obj):
        return obj.meeting.title

    def get_channel_name(self, obj):
        return obj.meeting.channel_name

    def get_sub_topics(self, obj):
        return json.loads(obj.meeting.sub_topics)

    def get_description(self, obj):
        return json.loads(obj.meeting.description)

    def get_host(self, obj):
        return (
            UserSerializer(obj.meeting.user).data
            if obj.meeting.user
            else {
                "id": 0,
                "nickname": "랜선동네모임",
                "profile_image_url": "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/logo.png",
                "manner_temperature": 36.5,
                "region_name": "교보타워",
            }
        )

    def get_start_time(self, obj):
        return obj.meeting.start_time

    def get_end_time(self, obj):
        return obj.meeting.end_time


class MeetingEnterCodeSerializer(serializers.ModelSerializer):
    meeting = MeetingLogSimpleSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = MeetingEnterCode
        fields = ["meeting", "user", "agora_token", "token", "code"]

    def get_token(self, obj):
        return obj.user.token
