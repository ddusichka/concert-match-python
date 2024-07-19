from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
import json
from django.core.serializers import serialize
from concerts.models import Concert
from tracks.models import Track
from .models import Match

# Create your views here.
def find_and_create_matches(request):
    for track in Track.objects.all():
        for concert in Concert.objects.filter(attraction_name=track.artist):
            # Ensure to specify concert and artist_name at creation
            match, created = Match.objects.get_or_create(
                concert=concert,
                artist_name=concert.attraction_name  # Assuming concert has an 'artist' attribute for artist name
            )
            # Now add the track to the match
            match.tracks.add(track)

    matches = Match.objects.all()
    matches_json = serialize('json', matches)
    parsed_data = json.loads(matches_json)  # Parse the JSON string into a Python object
    return JsonResponse(parsed_data, safe=False, json_dumps_params={'indent': 4})


def get_all_match_details(request):
    matches = Match.objects.all()
    detailed_matches = []

    for match in matches:
        concert_details = Concert.objects.filter(id=match.concert.id).values()
        track_details = Track.objects.filter(id__in=match.tracks.all()).values()

        detailed_match = {
            'model': 'matches.match',
            'pk': match.id,
            'fields': {
                'concert': list(concert_details),
                'artist_name': match.artist_name,
                'tracks': list(track_details)
            }
        }
        detailed_matches.append(detailed_match)

    return JsonResponse(detailed_matches, safe=False, json_dumps_params={'indent': 4})