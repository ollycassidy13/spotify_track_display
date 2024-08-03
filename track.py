import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

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
            return f"{track_name} - {artists}"
        else:
            return "No music playing"
    except Exception as e:
        return f"Error fetching data: {e}"

if __name__ == "__main__":
    last_track_info = ""
    while True:
        track_info = get_current_track()
        if track_info != last_track_info:
            print(track_info)
            last_track_info = track_info
        time.sleep(2)  
