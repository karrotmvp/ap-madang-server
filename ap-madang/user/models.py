from django.db import models


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(Base):
    karrot_user_id = models.CharField(max_length=200, unique=True)
    nickname = models.CharField(max_length=200)
    profile_image_url = models.TextField(blank=True, null=True)
    manner_point = models.IntegerField()
    manner_temperature = models.FloatField(blank=True, null=True)
    token = models.CharField(max_length=400)
    region_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nickname

    class Meta:
        indexes = [models.Index(fields=["token"])]
