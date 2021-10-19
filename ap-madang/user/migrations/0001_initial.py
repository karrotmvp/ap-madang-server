# Generated by Django 3.2.7 on 2021-10-13 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('karrot_user_id', models.CharField(max_length=200, unique=True)),
                ('nickname', models.CharField(max_length=200)),
                ('profile_image_url', models.TextField(blank=True, null=True)),
                ('temperature', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
