# Generated by Django 3.2.7 on 2021-10-22 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarmtalk', '0002_alter_usermeetingalarm_meeting'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='usermeetingalarm',
            constraint=models.UniqueConstraint(fields=('user', 'meeting'), name='only one alarm for each meeting - user'),
        ),
    ]
