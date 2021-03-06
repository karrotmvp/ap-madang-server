from django.db import models
from user.models import User
from meeting.models import MeetingLog


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserOpinion(Base):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)


class MeetingReview(Base):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    meeting = models.ForeignKey(
        MeetingLog, on_delete=models.SET_NULL, blank=True, null=True
    )
    body = models.TextField(blank=True, null=True)
