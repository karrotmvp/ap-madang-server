from django.db import models
from user.models import User
from meeting.models import Meeting

# Create your models here.
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserMeetingAlarm(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.nickname + " - " + self.meeting.title
