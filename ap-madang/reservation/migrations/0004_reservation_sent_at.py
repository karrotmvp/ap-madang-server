# Generated by Django 3.2.7 on 2021-10-18 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0003_reservation_suggestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]