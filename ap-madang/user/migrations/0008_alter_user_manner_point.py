# Generated by Django 3.2.7 on 2021-11-18 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_user_region_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='manner_point',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
