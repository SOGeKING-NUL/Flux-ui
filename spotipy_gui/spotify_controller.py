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
     
def get_library(sp):
    """
    Retrieve the current user's playlists and saved albums from Spotify.

    Args:
        sp: An authenticated Spotipy client instance.

    Returns:
        A tuple (playlist_links, album_links) where:
            - playlist_links is a dict mapping a playlist's Spotify URL to its name.
            - album_links is a dict mapping an album's Spotify URL to its name.
    """
    # Get playlists as a dict mapping URL -> name
    playlist_links = {}
    results = sp.current_user_playlists(limit=50)
    while results:
        for playlist in results.get('items', []):
            # Get the Spotify URL and name for each playlist
            url = playlist.get('external_urls', {}).get('spotify')
            if url:
                playlist_links[url] = playlist.get('name', 'Unknown')
        # Get the next page of results if available
        results = sp.next(results) if results.get('next') else None

    # Get saved albums as a dict mapping URL -> name
    album_links = {}
    results = sp.current_user_saved_albums(limit=50)
    while results:
        for item in results.get('items', []):
            album = item.get('album', {})
            url = album.get('external_urls', {}).get('spotify')
            if url:
                album_links[url] = album.get('name', 'Unknown')
        # Get the next page of results if available
        results = sp.next(results) if results.get('next') else None

    return playlist_links, album_links


def play_context_by_url(sp, url, device_name="PiPiece"):
    """
    Given a Spotify URL for a playlist or album, convert it to the corresponding Spotify
    context URI and start playback for that context.

    Args:
        sp: An authenticated Spotipy client instance.
        url: A Spotify URL (e.g., 'https://open.spotify.com/playlist/xxx' or 'https://open.spotify.com/album/xxx').
        device_name: The device to transfer playback to (default is "PiPiece").

    Returns:
        A message indicating whether playback was successfully started or if an error occurred.
    """
    # Transfer playback to the desired device (assumes activate_spotifyd_device is defined)
    transfer_message = activate_spotifyd_device(device_name)
    print(transfer_message)

    # Remove any query parameters (e.g., '?si=...') from the URL.
    base_url = url.split('?')[0]

    # Convert the URL to a Spotify URI.
    # Example: "https://open.spotify.com/playlist/abc123" becomes "spotify:playlist:abc123"
    context_uri = base_url.replace("https://open.spotify.com/", "spotify:").replace("/", ":")

    try:
        sp.start_playback(context_uri=context_uri)
        return f"Playback started for context: {context_uri}"
    except Exception as e:
        return f"Failed to start playback: {e}"