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
        fields = ["user", "meeting", "agora_token", "created_at"]


class MeetingLogSerializer(serializers.ModelSerializer):
    live_status = serializers.SerializerMethodField()
    alarm_id = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user_enter_cnt = serializers.SerializerMethodField()

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
            "image",
            "user_enter_cnt",
        ]

    def get_title(self, obj):
        return obj.meeting.title

    def get_start_time(self, obj):
        return obj.meeting.start_time

    def get_end_time(self, obj):
        return obj.meeting.end_time

    def get_image(self, obj):
        if obj.meeting.image:
            return obj.meeting.image.url
        return None

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
        return obj.alarm_id

    def get_user_enter_cnt(self, obj):
        cnt = obj.user_enter_cnt
        return 0 if cnt is None else cnt


class MeetingLogDetailSerializer(MeetingLogSerializer):
    description = serializers.SerializerMethodField()
    meeting_url = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    alarm_num = serializers.SerializerMethodField()
    channel_name = serializers.SerializerMethodField()

    def get_description(self, obj):
        return json.loads(obj.meeting.description)

    def get_meeting_url(self, obj):
        return obj.meeting.meeting_url

    def get_region(self, obj):
        return obj.meeting.region

    def get_alarm_num(self, obj):
        return UserMeetingAlarm.objects.filter(sent_at=None, meeting=obj).count()

    def get_channel_name(self, obj):
        return obj.meeting.channel_name

    class Meta(MeetingLogSerializer.Meta):
        fields = MeetingLogSerializer.Meta.fields + [
            "description",
            "meeting_url",
            "region",
            "alarm_num",
            "channel_name",
        ]
