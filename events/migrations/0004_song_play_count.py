# Generated by Django 3.2.9 on 2021-12-22 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='play_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
