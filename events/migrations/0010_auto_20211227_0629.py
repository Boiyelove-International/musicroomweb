# Generated by Django 3.2.9 on 2021-12-27 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20211224_0720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='suggestion_count',
        ),
        migrations.AddField(
            model_name='songsuggestion',
            name='accepted',
            field=models.BooleanField(null=True),
        ),
    ]
