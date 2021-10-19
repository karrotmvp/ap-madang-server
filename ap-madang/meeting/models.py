from django.db import models
from user.models import User
from datetime import datetime
import os
from uuid import uuid4


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    meeting_url = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=path_and_rename)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " - " + self.region


class UserMeetingEnter(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.nickname + " - " + self.meeting.title
