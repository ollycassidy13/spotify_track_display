import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import time
from PIL import Image
from io import BytesIO

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')

CLIENT_ID = config['spotify']['client_id']
CLIENT_SECRET = config['spotify']['client_secret']
REDIRECT_URI = config['spotify']['redirect_uri']

# Scope for accessing the currently playing track
SCOPE = 'user-read-playback-state'

# Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

def get_current_track():
    try:
        current_track = sp.current_playback()
        if current_track and current_track['is_playing']:
            track_name = current_track['item']['name']
            artists = ", ".join(artist['name'] for artist in current_track['item']['artists'])
            album_cover_url = current_track['item']['album']['images'][0]['url']
            return f"{track_name} - {artists}", album_cover_url
        else:
            return "No music playing", None
    except Exception as e:
        return f"Error fetching data: {e}", None

def get_dominant_color(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((1, 1))
        dominant_color = img.getpixel((0, 0))
        return dominant_color
    except Exception as e:
        print(f"Error fetching album cover: {e}")
        return (255, 0, 0)  # default to red in case of error

if __name__ == "__main__":
    last_track_info = ""
    while True:
        track_info, album_cover_url = get_current_track()
        if track_info != last_track_info:
            if album_cover_url:
                color = get_dominant_color(album_cover_url)
                color_hex = '#%02x%02x%02x' % color
            else:
                color_hex = '#ff0000'  # red color for no music playing

            print(f"Track Info: {track_info}")
            print(f"Dominant Color: {color_hex}")
            last_track_info = track_info
        time.sleep(2)
