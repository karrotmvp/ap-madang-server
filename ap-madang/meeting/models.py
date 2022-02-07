from django.db import models
from user.models import User
from datetime import datetime, timedelta
import os
from uuid import uuid4
import json
from django.core.exceptions import ValidationError
import random
import string


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Days(models.Model):
    DAY_CHOICES = (
        ("0_MON", "월"),
        ("1_TUE", "화"),
        ("2_WED", "수"),
        ("3_THUR", "목"),
        ("4_FRI", "금"),
        ("5_SAT", "토"),
        ("6_SUN", "일"),
    )
    day = models.CharField(max_length=8, choices=DAY_CHOICES, unique=True)

    def __str__(self):
        return self.day


def path_and_rename(instance, filename):
    upload_to = "meeting_image"
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        filename = "{}{}.{}".format(datetime.now(), instance.pk, ext)
    else:
        # set filename as random string
        filename = "{}{}.{}".format(datetime.now(), uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def create_channel_name():
    return (
        str(datetime.now())
        + "_"
        + "".join(random.choices(string.ascii_letters + string.digits, k=20))
    )


class Meeting(Base):
    title = models.TextField()
    description = models.TextField(
        blank=True,
        null=True,
        default='{"text" : "", "recommend_user": [{"text": ""}],"recommend_topic": [{"text": ""}]}',
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    region = models.CharField(max_length=200)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    days = models.ManyToManyField(Days, blank=True, null=True)
    meeting_url = models.TextField(blank=True, null=True)
    channel_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=path_and_rename)
    is_deleted = models.BooleanField(default=False)
    is_video = models.BooleanField(default=False)
    sub_topics = models.TextField(default="[]")
    thumbnail_image_url = models.CharField(max_length=400, blank=True, null=True)
    is_link = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["thumbnail_image_url"])]

    def save(self, *args, **kwargs):
        if not self.id:
            # 새로운 모임인 경우에, 채널 이름 생성
            self.channel_name = create_channel_name()
        return super(Meeting, self).save(*args, **kwargs)

    def clean(self):
        try:
            json.loads(self.description)
            json.loads(self.sub_topics)
        except:
            raise ValidationError("Description/Sub Topics format is not JSON!")

    def __str__(self):
        return self.title[:15] + " - " + self.region


class MeetingLog(Base):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    alarm_cnt_fake = models.IntegerField(default=0)
    enter_cnt_fake = models.IntegerField(default=0)
    alarm_fake_add_cnt = models.IntegerField(default=0)
    agora_user_list = models.TextField(default="[]")
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "date"], name="only one meeting for each day"
            ),
        ]

    def __str__(self):
        return (
            self.meeting.title[:15]
            + " - "
            + self.meeting.region
            + " at "
            + str(self.date)
        )

    def get_meeting_end_datetime(self):
        if self.meeting.start_time > self.meeting.end_time:
            return datetime.combine(
                self.date + timedelta(days=1), self.meeting.end_time
            )
        return datetime.combine(self.date, self.meeting.end_time)


class UserMeetingEnter(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(MeetingLog, on_delete=models.CASCADE)
    meeting_review_alarm_sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "user"], name="user has already entered"
            ),
        ]

    def __str__(self):
        return self.user.nickname + " - " + self.meeting.meeting.title[:15]
