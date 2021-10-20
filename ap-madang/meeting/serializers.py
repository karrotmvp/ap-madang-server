from rest_framework import serializers
from .models import *
from datetime import datetime
from alarmtalk.models import UserMeetingAlarm
import json
from .utils import *


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["title", "start_time", "end_time"]


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


class MeetingLogSerializer(serializers.ModelSerializer):
    live_status = serializers.SerializerMethodField()
    alarm_id = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = MeetingLog
        fields = [
            "id",
            "date",
            "live_status",
            "alarm_id",
            "title",
            "start_time",
            "end_time",
        ]

    def get_title(self, obj):
        return obj.meeting.title

    def get_start_time(self, obj):
        return obj.meeting.start_time

    def get_end_time(self, obj):
        return obj.meeting.end_time

    def get_live_status(self, obj):
        now = datetime.now().time()
        start = obj.meeting.start_time
        end = obj.meeting.end_time
        if obj.date != date.today():
            return "tomorrow"
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


class MeetingLogDetailSerializer(MeetingLogSerializer):
    end_time = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    meeting_url = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_description(self, obj):
        return json.loads(obj.meeting.description)

    def get_meeting_url(self, obj):
        return obj.meeting.meeting_url

    def get_region(self, obj):
        return obj.meeting.region

    def get_image(self, obj):
        return obj.meeting.image.url

    class Meta(MeetingLogSerializer.Meta):
        fields = MeetingLogSerializer.Meta.fields + [
            "description",
            "meeting_url",
            "region",
            "image",
        ]
