# Generated by Django 3.2.7 on 2021-11-10 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0013_auto_20211110_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='channel_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]