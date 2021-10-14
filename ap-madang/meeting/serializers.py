from rest_framework import serializers
from .models import *
from datetime import datetime


class MeetingSerializer(serializers.ModelSerializer):
    is_live = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ["id", "title", "start_time", "end_time", "is_live"]

    def get_is_live(self, obj):
        now = datetime.now().time()
        start = obj.start_time
        end = obj.end_time
        if start > end:
            return now >= start or now < end
        return start <= now < end


class MeetingDetailSerializer(MeetingSerializer):
    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + [
            "description",
            "meeting_url",
            "region",
        ]
