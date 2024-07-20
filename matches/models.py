from django.db import models

class Match(models.Model):
    concert = models.ForeignKey('concerts.Concert', on_delete=models.CASCADE)
    artist_name = models.CharField(max_length=255)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    tracks = models.ManyToManyField('tracks.Track')

class Favorite(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'match')