
import json
from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.core.serializers import serialize
from concerts.models import Concert
from tracks.models import Track, User
from .models import Favorite, Match
from .serializers import ConcertSerializer, TrackSerializer


# Create your views here.
def create_matches(request, user_id):
    for track in Track.objects.all():
        for concert in Concert.objects.filter(attraction_name=track.artist):
            user = User.objects.get(username=user_id)
            # Ensure to specify concert and artist_name at creation
            match, created = Match.objects.get_or_create(
                concert=concert,
                artist_name=concert.attraction_name,  # Assuming concert has an 'artist' attribute for artist name
                user=user
            )
            # Now add the track to the match
            match.tracks.add(track)

    matches = Match.objects.all()
    matches_json = serialize('json', matches)
    parsed_data = json.loads(matches_json)  # Parse the JSON string into a Python object
    return JsonResponse(parsed_data, safe=False, json_dumps_params={'indent': 4})

def get_all_match_details(request, user_id):
    matches = Match.objects.filter(user_id=user_id).order_by('concert__local_date')
    detailed_matches = []

    for match in matches:
        concert_details = Concert.objects.get(id=match.concert.id)
        track_qs = Track.objects.filter(id__in=match.tracks.all())

        # Group tracks by album
        albums = {}
        for track in track_qs:
            album_name = track.album
            if album_name not in albums:
                albums[album_name] = {
                    "artist": track.artist,
                    "image_url": track.image_url,
                    "tracks": [],
                    "release_date": track.release_date
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
                "release_date": details["release_date"],
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

def get_favorite_matches_for_user(request, user_id):
    favorite_matches = Match.objects.filter(favorite__user_id=user_id)
    favorite_matches_json = serialize('json', favorite_matches)
    parsed_data = json.loads(favorite_matches_json)  # Parse the JSON string into a Python object
    return JsonResponse(parsed_data, safe=False, json_dumps_params={'indent': 4})

def favorite_match(request, user_id, match_id):
    match = Match.objects.get(id=match_id)
    user = User.objects.get(id=user_id)

    favorite, created = Favorite.objects.get_or_create(user=user, match=match)
    if created:
        return JsonResponse({'message': 'Match favorited successfully'}, status=201)
    else:
        return JsonResponse({'message': 'Match already favorited'}, status=200)