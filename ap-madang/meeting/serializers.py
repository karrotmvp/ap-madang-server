from rest_framework import serializers
from .models import *
from datetime import datetime
from alarmtalk.models import UserMeetingAlarm
import json


class MeetingSerializer(serializers.ModelSerializer):
    live_status = serializers.SerializerMethodField()
    alarm_id = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ["id", "title", "start_time", "end_time", "live_status", "alarm_id"]

    def get_live_status(self, obj):
        now = datetime.now().time()
        start = obj.start_time
        end = obj.end_time
        if (start <= now < end) or (start > end and (now >= start or now < end)):
            return "live"
        if now < start:
            return "upcoming"
        return "finish"

    def get_alarm_id(self, obj):
        user = self.context["request"].user
        alarm = UserMeetingAlarm.objects.filter(sent_at=None, user=user, meeting=obj)
        if alarm:
            return alarm.first().id
        return None


class MeetingDetailSerializer(MeetingSerializer):
    description = serializers.SerializerMethodField()

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + [
            "description",
            "meeting_url",
            "region",
            "image",
        ]

    def get_description(self, obj):
        return json.loads(obj.description)


class UserMeetingEnterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMeetingEnter
        fields = ["user", "meeting", "created_at"]
