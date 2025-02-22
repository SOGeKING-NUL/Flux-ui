from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

class NewReleasesScreen(Screen):
    def on_enter(self):
        """Fetch and display new releases when the screen is entered."""
        self.fetch_new_releases()

    def fetch_new_releases(self):
        """Fetch new releases from Spotify and update the UI."""
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="user-library-read"
        ))

        results = sp.new_releases(limit=10)  # Fetch 10 new releases
        new_releases = results.get("albums", {}).get("items", [])

        self.update_ui(new_releases)

    @mainthread
    def update_ui(self, new_releases):
        """Update the UI with fetched new releases."""
        new_releases_list = self.ids.new_releases_list
        new_releases_list.clear_widgets()

        for album in new_releases:
            album_name = album["name"]
            artist_name = album["artists"][0]["name"]
            image_url = album["images"][0]["url"] if album["images"] else ""

            btn = self.create_album_button(album_name, artist_name)
            new_releases_list.add_widget(btn)

    def create_album_button(self, album_name, artist_name):
        """Create a button for each album."""
        from kivy.uix.button import Button

        btn = Button(
            text=f"{album_name} - {artist_name}",
            size_hint_y=None,
            height=50,
            color=(0, 1, 0, 1),  # Green text
            background_color=(0, 0, 0, 0),  # Transparent background
            on_release=lambda x: self.play_new_release(album_name, artist_name)
        )

        btn.bind(on_press=self.on_hover)
        btn.bind(on_release=self.on_unhover)

        return btn

    def play_new_release(self, album_name, artist_name):
        """Handle playing a new release (functionality to be added later)."""
        print(f"Playing {album_name} by {artist_name}")

    def on_hover(self, instance):
        """Change color when hovered over."""
        instance.color = (0, 0, 0, 1)  # Black text
        instance.background_color = (0, 1, 0, 0.5)  # Green background

    def on_unhover(self, instance):
        """Revert colors when not hovered."""
        instance.color = (0, 1, 0, 1)  # Green text
        instance.background_color = (0, 0, 0, 0)  # Transparent background
