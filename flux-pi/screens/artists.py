from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyOAuth

class ArtistsScreen(Screen):
    artists = ListProperty([])  # List to store artist names

    def on_pre_enter(self):
        """Fetch the user's followed artists before entering the screen."""
        self.fetch_artists()

    def fetch_artists(self):
        """Fetch the user's liked artists using Spotify API."""
        sp = Spotify(auth_manager=SpotifyOAuth(scope="user-follow-read"))
        results = sp.current_user_followed_artists(limit=20)
        self.artists = [artist['name'] for artist in results['artists']['items']]
        self.update_ui()
    
    def update_ui(self):
        """Update the UI with the fetched artists."""
        self.ids.artists_list.clear_widgets()
        for artist in self.artists:
            self.ids.artists_list.add_widget(ArtistRow(text=artist))
