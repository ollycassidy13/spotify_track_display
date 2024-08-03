import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
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

# Initialize LED matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 2  
options.cols = 64
options.hardware_mapping = 'regular'  
matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont("rpi-rgb-led-matrix/fonts/7x13.bdf")
textColor = graphics.Color(255, 0, 0)

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

def display_message(message):
    offscreen_canvas = matrix.CreateFrameCanvas()
    pos = offscreen_canvas.width
    while True:
        offscreen_canvas.Clear()
        len = graphics.DrawText(offscreen_canvas, font, pos, 20, textColor, message)
        pos -= 1
        if (pos + len < 0):
            pos = offscreen_canvas.width

        time.sleep(0.05)
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

if __name__ == "__main__":
    last_track_info = ""
    while True:
        track_info = get_current_track()
        if track_info != last_track_info:
            display_message(track_info)
            last_track_info = track_info
        time.sleep(2)  