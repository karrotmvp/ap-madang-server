# Generated by Django 3.2.7 on 2021-11-12 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0018_meeting_sub_topics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='sub_topics',
            field=models.TextField(default='[]'),
        ),
    ]