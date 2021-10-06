from django.db import models

# Create your models here.

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Reservation(Base):
    userid = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    suggestion = models.TextField(blank=True, null=True)
