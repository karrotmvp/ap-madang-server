from rest_framework import serializers
from .models import *
from datetime import datetime
from alarmtalk.models import UserMeetingAlarm
import json
from .utils import *
from user.serializers import *
from django.db.models import OuterRef, Subquery, Count


class MeetingSerializer(serializers.ModelSerializer):
    # description = serializers.JSONField()

    class Meta:
        model = Meeting
        fields = [
            "title",
            "description",
            "user",
            "region",
            "start_time",
            "end_time",
            "image",
            "is_video",
        ]


# class MeetingDetailSerializer(MeetingSerializer):
#     description = serializers.SerializerMethodField()

#     class Meta(MeetingSerializer.Meta):
#         fields = MeetingSerializer.Meta.fields + [
#             "description",
#             "meeting_url",
#             "region",
#             "image",
#         ]

#     def get_description(self, obj):
#         return json.loads(obj.description)


class UserMeetingEnterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMeetingEnter
        fields = ["user", "meeting", "created_at"]


class MeetingRecommendSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user_enter_cnt = serializers.SerializerMethodField()

    class Meta:
        model = MeetingLog
        fields = ["title", "image", "user_enter_cnt"]

    def get_title(self, obj):
        return obj.meeting.title

    def get_image(self, obj):
        if obj.meeting.image:
            return obj.meeting.image.url
        return None

    def get_user_enter_cnt(self, obj):
        cnt = obj.user_enter_cnt
        fake = obj.enter_cnt_fake
        return fake if cnt is None else (cnt + fake)


class MeetingLogSerializer(MeetingRecommendSerializer):
    live_status = serializers.SerializerMethodField()
    alarm_id = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    is_video = serializers.SerializerMethodField()

    class Meta(MeetingRecommendSerializer.Meta):
        model = MeetingLog
        fields = MeetingRecommendSerializer.Meta.fields + [
            "id",
            "date",
            "live_status",
            "alarm_id",
            "start_time",
            "end_time",
            "is_video",
        ]

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
        return obj.alarm_id

    def get_is_video(self, obj):
        return obj.meeting.is_video


class MeetingLogDetailSerializer(MeetingLogSerializer):
    description = serializers.SerializerMethodField()
    meeting_url = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    alarm_num = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    recommend = serializers.SerializerMethodField()

    def get_description(self, obj):
        return json.loads(obj.meeting.description)

    def get_meeting_url(self, obj):
        return obj.meeting.meeting_url

    def get_region(self, obj):
        return obj.meeting.region

    def get_user(self, obj):
        return UserSerializer(obj.meeting.user).data if obj.meeting.user else None

    def get_alarm_num(self, obj):
        return (
            UserMeetingAlarm.objects.filter(sent_at=None, meeting=obj).count()
            + obj.alarm_cnt_fake
        )

    def get_recommend(self, obj):
        def check_live(obj):
            now = datetime.now().time()
            start = obj.meeting.start_time
            end = obj.meeting.end_time
            if (start <= now < end) or (start > end and (now >= start or now < end)):
                return True
            return False

        meeting_logs = (
            MeetingLog.objects.filter(
                meeting__is_deleted=False,
                meeting__region=obj.meeting.region,
                date=date.today(),
            )
            .exclude(id=obj.id)
            .annotate(
                user_enter_cnt=Subquery(
                    UserMeetingEnter.objects.filter(meeting=OuterRef("pk"))
                    .values("meeting")
                    .annotate(count=Count("meeting"))
                    .values("count")
                )
            )
            .select_related("meeting")
        )
        meeting_logs = list(filter(check_live, meeting_logs))
        return MeetingRecommendSerializer(meeting_logs, many=True).data

    class Meta(MeetingLogSerializer.Meta):
        fields = MeetingLogSerializer.Meta.fields + [
            "description",
            "meeting_url",
            "region",
            "alarm_num",
            "user",
            "recommend",
        ]
