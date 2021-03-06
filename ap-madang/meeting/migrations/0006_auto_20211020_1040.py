# Generated by Django 3.2.7 on 2021-10-20 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0005_alter_meeting_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Days',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('MON', '월'), ('TUE', '화'), ('WED', '수'), ('THUR', '목'), ('FRI', '금'), ('SAT', '토'), ('SUN', '일')], max_length=8)),
            ],
        ),
        migrations.AddField(
            model_name='meeting',
            name='days',
            field=models.ManyToManyField(to='meeting.Days'),
        ),
    ]
