from django.db import models
from user.models import User


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    image = models.ImageField(blank=True, null=True, upload_to="meeting_image")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " - " + self.region


class UserMeetingEnter(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.nickname + " - " + self.meeting.title
