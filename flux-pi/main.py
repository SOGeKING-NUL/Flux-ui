# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
import os

# Import all screens
from screens.home import HomeScreen
from screens.artists import ArtistsScreen
from screens.albums import AlbumsScreen
from screens.new_releases import NewReleasesScreen
from screens.playlists import PlaylistsScreen
from screens.search import SearchScreen

# Load KV files
KV_PATH = "kv"
for kv_file in os.listdir(KV_PATH):
    if kv_file.endswith(".kv"):
        Builder.load_file(os.path.join(KV_PATH, kv_file))

class FluxApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"  # Theme color for consistency
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ArtistsScreen(name="artists"))
        sm.add_widget(AlbumsScreen(name="albums"))
        sm.add_widget(NewReleasesScreen(name="new_releases"))
        sm.add_widget(PlaylistsScreen(name="playlists"))
        sm.add_widget(SearchScreen(name="search"))
        return sm

if __name__ == "__main__":
    FluxApp().run()
