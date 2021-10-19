from rest_framework import serializers
from .models import *


class UserMeetingAlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMeetingAlarm
        fields = ["id", "meeting", "user", "created_at"]
