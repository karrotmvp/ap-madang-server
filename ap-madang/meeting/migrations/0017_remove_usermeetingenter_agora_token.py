# Generated by Django 3.2.7 on 2021-11-11 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0016_meeting_is_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermeetingenter',
            name='agora_token',
        ),
    ]