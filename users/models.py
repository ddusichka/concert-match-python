from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    display_name = models.CharField(max_length=255)
    last_spotify_import = models.DateTimeField(null=True)
    markets = models.ManyToManyField('concerts.Market')

    def __str__(self):
        return self.username