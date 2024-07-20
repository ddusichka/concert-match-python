
import json
from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.core.serializers import serialize
from concerts.models import Concert
from tracks.models import Track
from .models import Match
from .serializers import ConcertSerializer, TrackSerializer


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
        concert_details = Concert.objects.get(id=match.concert.id)
        track_qs = Track.objects.filter(id__in=match.tracks.all())

        # Group tracks by album
        albums = {}
        for track in track_qs:
            album_name = track.album  # Assuming 'album' is a field on Track model
            if album_name not in albums:
                albums[album_name] = {
                    "artist": track.artist,  # Assuming 'artist' is a field on Track model
                    "image_url": track.image_url,  # Assuming 'image_url' is a field on Track model
                    "tracks": []
                }
            albums[album_name]["tracks"].append(track)

        # Serialize tracks for each album and prepare album details
        albums_list = []
        for album_name, details in albums.items():
            serialized_tracks = TrackSerializer(details["tracks"], many=True).data
            album_details = {
                "name": album_name,
                "artist": details["artist"],
                "image_url": details["image_url"],
                "tracks": serialized_tracks
            }
            albums_list.append(album_details)

        detailed_match = {
            'id': match.id,
            'concert': ConcertSerializer(concert_details).data,
            'artist_name': match.artist_name,
            'albums': albums_list
        }
        detailed_matches.append(detailed_match)

    return JsonResponse(detailed_matches, safe=False, json_dumps_params={'indent': 4})