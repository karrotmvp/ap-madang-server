# Generated by Django 3.2.7 on 2021-11-11 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0015_auto_20211110_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='is_video',
            field=models.BooleanField(default=True),
        ),
    ]
