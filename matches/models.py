from django.db import models

class Match(models.Model):
    concert = models.ForeignKey('concerts.Concert', on_delete=models.CASCADE)
    artist_name = models.CharField(max_length=255)
    tracks = models.ManyToManyField('tracks.Track')