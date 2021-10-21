from django.db import models
from django.db.models.constraints import UniqueConstraint
from user.models import User
from datetime import datetime
import os
from uuid import uuid4


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


class Meeting(Base):
    title = models.TextField()
    description = models.TextField(
        blank=True,
        null=True,
        default='{"text" : "", "recommend_user": [{"text": ""}],"recommend_topic": [{"text": ""}]}',
    )
    region = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    days = models.ManyToManyField(Days, blank=True)
    meeting_url = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=path_and_rename)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " - " + self.region


class MeetingLog(Base):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "date"], name="only one meeting for each day"
            ),
        ]

    def __str__(self):
        return (
            self.meeting.title + " - " + self.meeting.region + " at " + str(self.date)
        )


class UserMeetingEnter(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.nickname + " - " + self.meeting.title
