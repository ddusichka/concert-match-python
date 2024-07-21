from django.db import models

class Concert(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    event_id = models.CharField(max_length=255, null=False, blank=False, unique=True)
    url = models.URLField(max_length=255, blank=True)
    image_url = models.URLField(max_length=255, null=False, blank=False)
    attraction_id = models.CharField(max_length=255, null=False, blank=False)
    attraction_name = models.CharField(max_length=255, null=False, blank=False)
    local_date = models.DateField(null=False, blank=False)
    local_time = models.TimeField(null=True, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    subgenre = models.CharField(max_length=255, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market = models.ForeignKey('Market', on_delete=models.CASCADE, null=True)
    venue = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, null=False, blank=False)
    state = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        # Adding timestamps
        get_latest_by = 'local_date'

class Market(models.Model):
    market_id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description