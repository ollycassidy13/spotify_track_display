import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import RPi.GPIO as GPIO
import logging
from logging.handlers import RotatingFileHandler

# Setup GPIO
RED_PIN = 17
ORANGE_PIN = 27
GREEN_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(ORANGE_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)

# Initialize logging with rotation
log_handler = RotatingFileHandler('/home/ollyj/track_display/track_log.txt', maxBytes=500000, backupCount=5)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[log_handler])

# Read config file
config = configparser.ConfigParser()
config.read('/home/ollyj/track_display/config.ini')

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
            track_id = current_track['item']['id']
            progress_ms = current_track['progress_ms'] / 1000.0
            return f"{track_name} - {artists}", track_id, progress_ms
        else:
            return "No music playing", None, None
    except Exception as e:
        return f"Error fetching data: {e}", None, None

def get_beat_times(track_id):
    try:
        analysis = sp.audio_analysis(track_id)
        beats = [beat['start'] for beat in analysis['beats']]
        return beats
    except Exception as e:
        print(f"Error fetching beat times: {e}")
        return []

def update_leds(state, beat_times=None, start_time=None):
    if state == "no_music":
        GPIO.output(RED_PIN, GPIO.HIGH)
        GPIO.output(ORANGE_PIN, GPIO.LOW)
        GPIO.output(GREEN_PIN, GPIO.LOW)
    elif state == "playing":
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(ORANGE_PIN, GPIO.LOW)
        if beat_times:
            current_time = time.time() - start_time
            next_beat_time = min((beat for beat in beat_times if beat >= current_time), default=None)
            if next_beat_time:
                GPIO.output(GREEN_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(GREEN_PIN, GPIO.LOW)
                time.sleep(next_beat_time - current_time)
    elif state == "error":
        GPIO.output(RED_PIN, GPIO.LOW)
        GPIO.output(ORANGE_PIN, GPIO.HIGH)
        GPIO.output(GREEN_PIN, GPIO.LOW)

if __name__ == "__main__":
    last_track_id = None
    beat_times = []
    start_time = None

    while True:
        track_info, track_id, progress_ms = get_current_track()
        if track_id != last_track_id:
            print(track_info)
            logging.info(track_info)
            last_track_id = track_id

            if "Error fetching data" in track_info:
                update_leds("error")
                beat_times = []
            elif track_info == "No music playing":
                update_leds("no_music")
                beat_times = []
            else:
                beat_times = get_beat_times(track_id)
                start_time = time.time() - progress_ms

        if beat_times:
            update_leds("playing", beat_times, start_time)
        
        time.sleep(0.1)  # Short delay
