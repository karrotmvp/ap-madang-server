# Generated by Django 3.2.7 on 2021-10-13 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='temperature',
            new_name='manner_point',
        ),
    ]
