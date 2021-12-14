from django.db import models

# Create your models here.
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ShareUrl(Base):
    origin_url = models.CharField(max_length=200)
    karrot_scheme_url = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=100)
    access_cnt = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["origin_url"]), models.Index(fields=["code"])]
