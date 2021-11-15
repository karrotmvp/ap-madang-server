from django.db import models
import datetime
import hashlib
from .AgoraDynamicKey.RtcTokenBuilder import *
from config.settings import AGORA_APP_ID, AGORA_APP_CERTIFICATE


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def create_meeting_enter_code(user_id, meeting_id):
    text = str(user_id) + str(meeting_id) + str(datetime.datetime.now())
    return hashlib.md5(text.encode()).hexdigest()


def create_agora_token(meeting, user):
    return RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID,
        AGORA_APP_CERTIFICATE,
        meeting.meeting.channel_name,
        user.id,
        Role_Attendee,
        datetime.datetime.combine(meeting.date, meeting.meeting.end_time).timestamp(),
    )


class MeetingEnterCode(Base):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    meeting = models.ForeignKey("meeting.MeetingLog", on_delete=models.CASCADE)
    code = models.TextField()
    agora_token = models.TextField()
    is_valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # 생성될 때마다 code, token 자동 생성 (수정되는 경우는 없어야함)
        self.code = create_meeting_enter_code(self.meeting.id, self.user.id)
        self.agora_token = create_agora_token(self.meeting, self.user)
        return super(MeetingEnterCode, self).save(*args, **kwargs)
