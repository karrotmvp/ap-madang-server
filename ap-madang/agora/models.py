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
    privilegeExpiredTs = (
        0 if meeting.meeting.is_link else meeting.get_meeting_end_datetime().timestamp()
    )

    return RtcTokenBuilder.buildTokenWithUid(
        AGORA_APP_ID,
        AGORA_APP_CERTIFICATE,
        meeting.meeting.channel_name,
        user.id,
        Role_Attendee,
        privilegeExpiredTs,
    )


class MeetingEnterCode(Base):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    meeting = models.ForeignKey("meeting.MeetingLog", on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    agora_token = models.CharField(max_length=300)
    is_valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # 생성될 때마다 code, token 자동 생성 (수정되는 경우는 없어야함)
            self.code = create_meeting_enter_code(self.meeting.id, self.user.id)
            self.agora_token = create_agora_token(self.meeting, self.user)
        return super(MeetingEnterCode, self).save(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=["code", "is_valid"])]
