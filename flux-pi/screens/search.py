from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.clock import Clock
import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

class SearchScreen(Screen):
    search_query = StringProperty("")

    def on_pre_enter(self, *args):
        self.ids.title.text = "Search"

    def search_music(self):
        """Triggers a search on Spotify API."""
        query = self.search_query.strip()
        if query:
            self.ids.search_results.clear_widgets()
            threading.Thread(target=self.fetch_search_results, args=(query,), daemon=True).start()

    def fetch_search_results(self, query):
        """Fetches search results from Spotify."""
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                       client_secret=SPOTIPY_CLIENT_SECRET,
                                                       redirect_uri=SPOTIPY_REDIRECT_URI,
                                                       scope="user-library-read"))

        results = sp.search(q=query, type='track,artist,album,playlist', limit=5)

        items = []
        for category in ['tracks', 'artists', 'albums', 'playlists']:
            if category in results and results[category]['items']:
                for item in results[category]['items']:
                    name = item['name'] if category != 'artists' else item['name']
                    items.append(name)

        Clock.schedule_once(lambda dt: self.display_results(items), 0)

    def display_results(self, items):
        """Displays search results in the UI."""
        for item in items:
            self.ids.search_results.add_widget(SearchResultButton(text=item))

class SearchResultButton(Screen):
    pass
