from django.db import models

# Create your models here.

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Reservation(Base):
    user_id = models.TextField(unique=True)
    nickname = models.TextField()
    region_id = models.BigIntegerField()