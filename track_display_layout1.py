import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import random

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

# Initialize LED matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 2  
options.cols = 64
options.hardware_mapping = 'regular'  
options.disable_hardware_pulsing = True
matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont("4x6.bdf")

def get_current_track():
    try:
        current_track = sp.current_playback()
        if current_track and current_track['is_playing']:
            track_name = current_track['item']['name']
            artists = ", ".join(artist['name'] for artist in current_track['item']['artists'])
            return track_name, artists
        else:
            return "No music playing", ""
    except Exception as e:
        return f"Error fetching data: {e}", ""

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def display_message(track_name, artists, textColor):
    offscreen_canvas = matrix.CreateFrameCanvas()
    pos = offscreen_canvas.width
    while True:
        offscreen_canvas.Clear()
        # Display the song title at the top
        len1 = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, track_name)
        # Display the artists' names below the song title
        len2 = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor, artists)
        
        pos -= 1
        if (pos + max(len1, len2) < 0):
            pos = offscreen_canvas.width

        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        # Check if the track info has changed every 2 seconds
        current_track_name, current_artists = get_current_track()
        if f"{current_track_name} - {current_artists}" != f"{track_name} - {artists}":
            break

if __name__ == "__main__":
    last_track_info = ""
    while True:
        track_name, artists = get_current_track()
        track_info = f"{track_name} - {artists}"
        if track_info != last_track_info:
            last_track_info = track_info
            color = get_random_color()
            textColor = graphics.Color(*color)
            display_message(track_name, artists, textColor)
        time.sleep(2)
