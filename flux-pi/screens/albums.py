from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from spotipy_client import SpotipyClient

class AlbumsScreen(Screen):
    albums = ListProperty([])  # Holds the list of liked albums

    def on_enter(self):
        """Fetch the user's liked albums when the screen is entered."""
        self.fetch_albums()

    def fetch_albums(self):
        """Fetch liked albums from the Spotify API."""
        sp = SpotipyClient()
        albums_data = sp.get_liked_albums()
        
        self.albums = [
            {'name': album['name'], 'artist': album['artists'][0]['name'], 'image': album['images'][0]['url']}
            for album in albums_data
        ]

    def select_album(self, album):
        """Handle selection of an album and navigate to its track list."""
        self.manager.get_screen('album_tracks').album = album  # Set album data
        self.manager.current = 'album_tracks'
