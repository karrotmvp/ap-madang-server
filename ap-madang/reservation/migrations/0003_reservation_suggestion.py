# Generated by Django 3.2.7 on 2021-10-06 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0002_rename_user_id_reservation_userid'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='suggestion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
