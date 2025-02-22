import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

class SpotifyAPI:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope="user-library-read user-read-playback-state user-modify-playback-state"
        ))

    def get_favorite_artists(self):
        """Fetches favorite artists of the user."""
        results = self.sp.current_user_top_artists(limit=10)
        return [artist['name'] for artist in results['items']]

    def get_liked_albums(self):
        """Fetches albums liked by the user."""
        results = self.sp.current_user_saved_albums(limit=10)
        return [album['album']['name'] for album in results['items']]

    def get_new_releases(self):
        """Fetches new releases from followed artists."""
        results = self.sp.new_releases(limit=10)
        return [album['name'] for album in results['albums']['items']]

    def get_liked_playlists(self):
        """Fetches liked playlists of the user."""
        results = self.sp.current_user_playlists(limit=10)
        return [playlist['name'] for playlist in results['items']]

    def search(self, query):
        """Search for a track, artist, album, or playlist."""
        results = self.sp.search(q=query, type='track,artist,album,playlist', limit=5)
        return results

