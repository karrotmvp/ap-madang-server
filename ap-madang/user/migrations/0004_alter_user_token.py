# Generated by Django 3.2.7 on 2021-11-15 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_user_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="token",
            field=models.CharField(max_length=400),
        ),
    ]
