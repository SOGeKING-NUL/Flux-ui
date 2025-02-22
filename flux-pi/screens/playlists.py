from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

class PlaylistsScreen(Screen):
    def on_enter(self):
        """Fetch and display user playlists when the screen is entered."""
        self.fetch_playlists()

    def fetch_playlists(self):
        """Fetch user's playlists from Spotify and update the UI."""
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private"
        ))

        results = sp.current_user_playlists()
        playlists = results.get("items", [])

        self.update_ui(playlists)

    @mainthread
    def update_ui(self, playlists):
        """Update the UI with fetched playlists."""
        playlists_list = self.ids.playlists_list
        playlists_list.clear_widgets()

        for playlist in playlists:
            playlist_name = playlist["name"]
            image_url = playlist["images"][0]["url"] if playlist["images"] else ""

            btn = self.create_playlist_button(playlist_name)
            playlists_list.add_widget(btn)

    def create_playlist_button(self, playlist_name):
        """Create a button for each playlist."""
        from kivy.uix.button import Button

        btn = Button(
            text=playlist_name,
            size_hint_y=None,
            height=50,
            color=(0, 1, 0, 1),  # Green text
            background_color=(0, 0, 0, 0),  # Transparent background
            on_release=lambda x: self.open_playlist(playlist_name)
        )

        btn.bind(on_press=self.on_hover)
        btn.bind(on_release=self.on_unhover)

        return btn

    def open_playlist(self, playlist_name):
        """Handle playlist selection (functionality to be added later)."""
        print(f"Opening playlist: {playlist_name}")

    def on_hover(self, instance):
        """Change color when hovered over."""
        instance.color = (0, 0, 0, 1)  # Black text
        instance.background_color = (0, 1, 0, 0.5)  # Green background

    def on_unhover(self, instance):
        """Revert colors when not hovered."""
        instance.color = (0, 1, 0, 1)  # Green text
        instance.background_color = (0, 0, 0, 0)  # Transparent background
