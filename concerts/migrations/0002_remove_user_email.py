# Generated by Django 4.0 on 2024-07-14 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concerts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='email',
        ),
    ]
