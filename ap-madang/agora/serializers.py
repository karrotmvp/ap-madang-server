from rest_framework import serializers
from agora.models import MeetingEnterCode
from user.serializers import UserSerializer
from meeting.models import MeetingLog
import json


class MeetingLogSimpleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    channel_name = serializers.SerializerMethodField()
    sub_topics = serializers.SerializerMethodField()

    class Meta:
        model = MeetingLog
        fields = ["id", "title", "channel_name", "sub_topics"]

    def get_title(self, obj):
        return obj.meeting.title

    def get_channel_name(self, obj):
        return obj.meeting.channel_name

    def get_sub_topics(self, obj):
        return json.loads(obj.meeting.sub_topics)


class MeetingEnterCodeSerializer(serializers.ModelSerializer):
    meeting = MeetingLogSimpleSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = MeetingEnterCode
        fields = ["meeting", "user", "agora_token"]
