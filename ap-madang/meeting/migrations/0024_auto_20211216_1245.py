# Generated by Django 3.2.7 on 2021-12-16 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0023_usermeetingenter_meeting_review_alarm_sent_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='thumbnail_image_url',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AddIndex(
            model_name='meeting',
            index=models.Index(fields=['thumbnail_image_url'], name='meeting_mee_thumbna_de1aa2_idx'),
        ),
    ]
