from django.db import models
from user.models import User
from meeting.models import MeetingLog

# Create your models here.
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserMeetingAlarm(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(MeetingLog, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "meeting"],
                name="only one alarm for each meeting - user",
            ),
        ]

    def __str__(self):
        return self.user.nickname + " - " + self.meeting.meeting.title
