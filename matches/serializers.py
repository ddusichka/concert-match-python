from rest_framework import serializers
from concerts.models import Concert
from tracks.models import Track

class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = '__all__'  # Or list specific fields you want to include

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'name', 'added_at']