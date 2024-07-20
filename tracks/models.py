from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    

class Track(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    image_url = models.URLField(max_length=255, blank=True)
    added_at = models.DateTimeField(auto_now_add=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    