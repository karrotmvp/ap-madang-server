from rest_framework import serializers
from .models import *
import json
from .utils import *
from user.serializers import *
from agora.views import is_agora_channel_available, get_agora_channel_user_cnt
from user.models import User
from config.settings import CLIENT_BASE_URL
from share.utils import create_meeting_short_url


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = [
            "title",
            "user",
            "region",
            "start_time",
            "end_time",
            "is_video",
            "description",
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
    # image = serializers.SerializerMethodField()
    # user_enter_cnt = serializers.SerializerMethodField()

    class Meta:
        model = MeetingLog
        fields = ["title"]

    def get_title(self, obj):
        return obj.meeting.title

    def get_image(self, obj):
        if obj.meeting.thumbnail_image_url:
            return obj.meeting.thumbnail_image_url
        if obj.meeting.image:
            return obj.meeting.image.url
        return None

    def get_user_enter_cnt(self, obj):
        cnt = obj.user_enter_cnt
        fake = obj.enter_cnt_fake
        return fake if cnt is None else (cnt + fake)


class MeetingLogSerializer(MeetingRecommendSerializer):
    live_status = serializers.SerializerMethodField()
    # alarm_id = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    is_video = serializers.SerializerMethodField()
    description_text = serializers.SerializerMethodField()
    # alarm_num = serializers.SerializerMethodField()
    is_host = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    agora_user_list = serializers.SerializerMethodField()
    meeting_url = serializers.SerializerMethodField()
    share_code = serializers.SerializerMethodField()

    class Meta(MeetingRecommendSerializer.Meta):
        model = MeetingLog
        common_fields = MeetingRecommendSerializer.Meta.fields + [
            "id",
            "date",
            "live_status",
            #    "alarm_id",
            "start_time",
            "end_time",
            "is_video",
            #    "alarm_num",
            "is_host",
            "host",
            "agora_user_list",
            "meeting_url",
            "share_code",
        ]
        fields = common_fields + ["description_text"]

    def get_start_time(self, obj):
        return obj.meeting.start_time

    def get_end_time(self, obj):
        return obj.meeting.end_time

    def get_live_status(self, obj):
        return obj.live_status

    def get_alarm_id(self, obj):
        user = self.context["request"].user
        if user is None:
            return None

        return obj.alarm_id

    def get_is_video(self, obj):
        return obj.meeting.is_video

    def get_description_text(self, obj):
        return json.loads(obj.meeting.description).get("text", None)

    def get_alarm_num(self, obj):
        # return (
        #     UserMeetingAlarm.objects.filter(sent_at=None, meeting=obj).count()
        #     + obj.alarm_cnt_fake
        # )
        cnt = obj.alarm_num
        fake = obj.alarm_cnt_fake
        return fake if cnt is None else (cnt + fake)

    def get_is_host(self, obj):
        user = self.context["request"].user
        if user is None:
            return False

        return user == obj.meeting.user

    def get_host(self, obj):
        return (
            UserSerializer(obj.meeting.user).data
            if obj.meeting.user
            else {
                "id": 0,
                "nickname": "랜선동네모임",
                "profile_image_url": "https://ap-madang-server.s3.ap-northeast-2.amazonaws.com/static/api/logo.png",
                "manner_temperature": 36.5,
                "region_name": "당근마켓",
            }
        )

    def get_agora_user_list(self, obj):
        if obj.live_status != "live" or obj.meeting.is_video:
            return list()
        agora_users_list = json.loads(obj.agora_user_list)
        users = User.objects.filter(id__in=agora_users_list)
        return SimpleUserSerializer(users, many=True).data

    def get_meeting_url(self, obj):
        return obj.meeting.meeting_url

    def get_share_code(self, obj):
        origin_url = "{}/?#/?meeting={}".format(CLIENT_BASE_URL, obj.id)
        url, code = create_meeting_short_url(origin_url, obj.id)
        return code


class MeetingLogDetailSerializer(MeetingLogSerializer):
    description = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    is_agora_channel_available = serializers.SerializerMethodField()
    # recommend = serializers.SerializerMethodField()

    def get_description(self, obj):
        return json.loads(obj.meeting.description)

    def get_region(self, obj):
        return obj.meeting.region

    # override get image to get original image
    def get_image(self, obj):
        if obj.meeting.image:
            return obj.meeting.image.url
        return None

    def get_is_agora_channel_available(self, obj):
        return is_agora_channel_available(obj.meeting.channel_name)

    # def get_recommend(self, obj):
    #     def check_live(obj):
    #         now = datetime.now().time()
    #         start = obj.meeting.start_time
    #         end = obj.meeting.end_time
    #         if (start <= now < end) or (start > end and (now >= start or now < end)):
    #             return True
    #         return False

    #     meeting_logs = (
    #         MeetingLog.objects.filter(
    #             meeting__is_deleted=False,
    #             meeting__region=obj.meeting.region,
    #             date=date.today(),
    #         )
    #         .exclude(id=obj.id)
    #         .annotate(
    #             user_enter_cnt=Subquery(
    #                 UserMeetingEnter.objects.filter(meeting=OuterRef("pk"))
    #                 .values("meeting")
    #                 .annotate(count=Count("meeting"))
    #                 .values("count")
    #             )
    #         )
    #         .select_related("meeting")
    #     )
    #     meeting_logs = list(filter(check_live, meeting_logs))
    #     return MeetingRecommendSerializer(meeting_logs, many=True).data

    class Meta(MeetingLogSerializer.Meta):
        fields = MeetingLogSerializer.Meta.common_fields + [
            "description",
            "region",
            "is_agora_channel_available"
            # "recommend",
        ]
