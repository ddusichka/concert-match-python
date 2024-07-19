# Generated by Django 4.0 on 2024-07-19 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tracks', '0001_initial'),
        ('concerts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist_name', models.CharField(max_length=255)),
                ('concert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concerts.concert')),
                ('tracks', models.ManyToManyField(to='tracks.Track')),
            ],
        ),
    ]
