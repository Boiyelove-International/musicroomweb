# Generated by Django 3.2.9 on 2021-12-17 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_emailaddress_passwordresetrequest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notifications',
        ),
    ]
