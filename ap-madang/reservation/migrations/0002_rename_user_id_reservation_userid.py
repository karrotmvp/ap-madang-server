# Generated by Django 3.2.7 on 2021-10-06 02:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='user_id',
            new_name='userid',
        ),
    ]
