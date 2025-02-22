import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

scope = ("user-library-modify user-library-read playlist-read-private "
         "playlist-modify-public playlist-modify-private user-modify-playback-state "
         "user-read-playback-state user-read-currently-playing")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                              client_secret=SPOTIPY_CLIENT_SECRET,
                                              redirect_uri=SPOTIPY_REDIRECT_URI,
                                              scope=scope))

# Decorator to ensure spotifyd (PiPiece) is active
def ensure_spotifyd_active(func):
    def wrapper(*args, **kwargs):
        activate_spotifyd_device("PiPiece")
        return func(*args, **kwargs)
    return wrapper

def activate_spotifyd_device(device_name):
    """
    Transfer playback to the device (running spotifyd) with the given name.
    """
    devices = sp.devices().get("devices", [])
    target_device = next((d for d in devices if d["name"] == device_name), None)
    if target_device is None:
        return f"Device '{device_name}' not found."
    device_id = target_device["id"]
    sp.transfer_playback(device_id, force_play=True)
    return f"Playback transferred to '{device_name}' (ID: {device_id})."

@ensure_spotifyd_active
def toggle_playback():
    current = sp.current_playback()
    if current and current["is_playing"]:
        sp.pause_playback()
        return "Playback paused."
    else:
        sp.start_playback()
        return "Playback resumed."

@ensure_spotifyd_active
def toggle_like_current_song():
    current = sp.current_playback()
    if current and current.get("item"):
        song_id = current["item"]["id"]
        liked = sp.current_user_saved_tracks_contains([song_id])[0]
        if liked:
            sp.current_user_saved_tracks_delete([song_id])
            return "Song removed from liked songs."
        else:
            sp.current_user_saved_tracks_add([song_id])
            return "Song liked!"
    return "No song is currently playing."

@ensure_spotifyd_active
def next_song():
    sp.next_track()
    return "Skipped to next song."

@ensure_spotifyd_active
def previous_song():
    sp.previous_track()
    return "Playing previous song."

@ensure_spotifyd_active
def toggle_shuffle():
    current = sp.current_playback()
    if current:
        current_shuffle = current.get("shuffle_state", False)
        new_shuffle = not current_shuffle
        sp.shuffle(new_shuffle)
        return f"Shuffle is now {'on' if new_shuffle else 'off'}."
    return "No song is playing."

@ensure_spotifyd_active
def toggle_loop():
    current = sp.current_playback()
    if current:
        repeat_state = current.get("repeat_state", "off")
        new_repeat = "track" if repeat_state == "off" else "off"
        sp.repeat(new_repeat)
        return f"Loop is now set to {new_repeat}."
    return "No song is playing."

def get_current_playback():
    """Helper function to get current playback state"""
    return sp.current_playback()

def is_track_liked(track_id):
    """Check if a track is saved in the user's library"""
    return sp.current_user_saved_tracks_contains([track_id])[0] 
     