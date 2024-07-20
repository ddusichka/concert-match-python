from django.utils import timezone
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from django.template.response import TemplateResponse
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

import credentials

from .models import Track, User  # Import the Track model
from django.shortcuts import render
import spotipy


def login(request):
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(client_id=credentials.client_ID, client_secret=credentials.client_SECRET, redirect_uri='http://localhost:8000/tracks/callback', scope = credentials.scope)

    # Print the sp_oauth object to the console
    print("\n\nSP_OAuth Object:" ,sp_oauth, "\n\n")

    # Redirect the user to the Spotify login page
    # Get the authorization URL
    url = sp_oauth.get_authorize_url()

    # Redirect the user to the Spotify login page
    return HttpResponseRedirect(url)

def callback(request):
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(client_id=credentials.client_ID, client_secret=credentials.client_SECRET, redirect_uri='http://localhost:8000/tracks/callback', scope=credentials.scope)

    # Get the authorization code from the query parameters
    code = request.GET.get("code")

    # Request an access token using the authorization code
    token_info = sp_oauth.get_access_token(code)

    # Extract the access token
    access_token = token_info["access_token"]

    # Store the access token in a secure way (e.g. in a session or database)
    request.session["access_token"] = access_token

    # Redirect the user to the top tracks page
    return HttpResponseRedirect("/tracks/top-tracks/")
    

@api_view(['GET'])
def get_top_tracks(request):
    if request.method == 'GET':
         # Get the access token from the session and create a Spotipy client
        access_token = request.session.get("access_token")
        sp = spotipy.Spotify(auth=access_token)

        # Make a request to the Spotify API to retrieve the user's profile information
        spotifyUser = sp.me()
        if spotifyUser is not None:
            user, created = User.objects.get_or_create(
                username=spotifyUser["id"], 
                display_name=spotifyUser["display_name"] 
            )
        else:
            print("The access token is invalid or has expired.\n\n")

        # Make the GET request to the Spotify API
        response = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")
        top_tracks = response["items"]

        return JsonResponse(top_tracks, safe=False)

    else:
        error = "An error has occurred"
        return error
    
@api_view(['GET'])
def import_all_tracks(request):
    if request.method == 'GET':
         # Get the access token from the session and create a Spotipy client
        # access_token = request.session.get("access_token")
            # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
        else:
            access_token = None

        if access_token is None:
            return JsonResponse({'error': 'No access token provided'}, status=401)

        sp = spotipy.Spotify(auth=access_token)

        # Make a request to the Spotify API to retrieve the user's profile information
        spotifyUser = sp.me()
        if spotifyUser is not None:
            user, created = User.objects.get_or_create(
                username=spotifyUser["id"], 
                display_name=spotifyUser["display_name"] 
            )
        else:
            print("The access token is invalid or has expired.\n\n")

        # Make the GET request to the Spotify API
        all_saved_tracks = []
        limit = 50
        offset = 0

        while True:
            response = sp.current_user_saved_tracks(market="US", limit=limit, offset=offset)
            tracks = response['items']
            if not tracks:
                break  # Exit the loop if no more tracks are returned
            all_saved_tracks.extend(tracks)
            if len(tracks) < limit:
                break  # Exit the loop if last page of tracks is fetched
            offset += limit  # Prepare offset for the next iteration

        delete_tracks_for_user(user.username)
        parse_saved_tracks(all_saved_tracks, user)
        User.objects.filter(username=spotifyUser["id"]).update(last_spotify_import=timezone.now())

        return JsonResponse(list(Track.objects.filter(user=user).values()), safe=False)
    else:
        error = "An error has occurred"
        return error

def delete_tracks_for_user(userId):
    try:
        user = User.objects.get(pk=userId)
    except User.DoesNotExist:
        return False

    Track.objects.filter(user=user).delete()
    return True  # Indicate success

def parse_saved_tracks(saved_tracks, user):
    for track in saved_tracks:
        for artist in track["track"]["artists"]:
            track_instance, created = Track.objects.get_or_create(
                name=track["track"]["name"], 
                artist=artist["name"], 
                album=track["track"]["album"]["name"],
                image_url=track["track"]["album"]["images"][0]["url"],
                added_at=track["added_at"],
                user=user
            )

            if created:
                print(f'Added new track: {track_instance.name}')