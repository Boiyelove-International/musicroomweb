# Generated by Django 3.2.9 on 2022-12-12 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_auto_20220107_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='apple_music_link',
            field=models.URLField(null=True),
        ),
    ]
