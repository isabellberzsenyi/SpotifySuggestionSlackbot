import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def create_spotify_client(cid, secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return sp