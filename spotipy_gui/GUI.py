#!/usr/bin/env python3
import threading
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ListProperty

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.snackbar import Snackbar

# Import your Spotify functions
from spotify_controller import (
    get_current_playback,
    toggle_playback,
    previous_song,
    next_song,
    toggle_like_current_song,
    is_track_liked,
    toggle_shuffle,
    toggle_loop
)
from spotify_controller import get_library, play_context_by_url, sp

# Set the initial window size to 240x320px
Window.size = (240, 320)
Window.clearcolor = (0, 0, 0, 1)

# -----------------------------------
# MarqueeLabel Implementation
# -----------------------------------
class MarqueeLabel(RelativeLayout):
    text = StringProperty("")
    font_size = NumericProperty("20sp")
    text_color = ListProperty([0, 1, 0, 1])
    delay = NumericProperty(2)  # seconds before starting marquee
    speed = NumericProperty(30) # pixels per second

    def __init__(self, **kwargs):
        super(MarqueeLabel, self).__init__(**kwargs)
        self.label = Label(text=self.text,
                           font_size=self.font_size,
                           color=self.text_color,
                           size_hint=(None, None))
        self.add_widget(self.label)
        self.bind(text=self._update_label,
                  font_size=self._update_label,
                  text_color=self._update_label,
                  size=self._update_label)
        Clock.schedule_once(self._start_marquee, self.delay)

    def _update_label(self, *args):
        self.label.text = self.text
        self.label.font_size = self.font_size
        self.label.color = self.text_color
        self.label.texture_update()
        self.label.width = self.label.texture_size[0]
        self.label.height = self.height
        self.label.x = self.width
        Clock.unschedule(self._marquee_update)
        if self.label.width > self.width:
            Clock.schedule_interval(self._marquee_update, 1/30.0)
        else:
            self.label.x = (self.width - self.label.width) / 2

    def on_size(self, *args):
        self._update_label()

    def _start_marquee(self, dt):
        if self.label.width > self.width:
            Clock.schedule_interval(self._marquee_update, 1/30.0)

    def _marquee_update(self, dt):
        self.label.x -= self.speed * dt
        if self.label.x < -self.label.width:
            self.label.x = self.width

# -----------------------------------
# KV Layout String
# -----------------------------------
KV = '''
#:import dp kivy.metrics.dp
#:import MarqueeLabel __main__.MarqueeLabel

<LibraryOverlay@BoxLayout>:
    orientation: "vertical"
    size_hint: None, None
    size: root.parent.width, root.parent.height
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDLabel:
        text: "Your Library"
        halign: "center"
        font_style: "Subtitle1"
        theme_text_color: "Custom"
        text_color: 0, 1, 0, 1
        size_hint_y: None
        height: dp(20)
        padding: dp(2), dp(2)
    ScrollView:
        MDList:
            id: library_list

<PlaySongPage@BoxLayout>:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(5)
    MDBoxLayout:
        orientation: "vertical"
        size_hint_y: 0.8
        spacing: dp(5)
        MDCard:
            size_hint: None, None
            size: root.width * 0.5, root.width * 0.5
            pos_hint: {"center_x": 0.5}
            elevation: 10
            radius: [dp(25),]
            AsyncImage:
                id: album_cover
                source: ""
                allow_stretch: True
                keep_ratio: True
        MarqueeLabel:
            id: song_title
            text: "Song Title"
            font_size: "18sp"
            size_hint_y: None
            height: dp(25)
        MarqueeLabel:
            id: song_artist
            text: "Artist"
            font_size: "14sp"
            size_hint_y: None
            height: dp(20)
        RelativeLayout:
            size_hint_y: None
            height: dp(40)
            MDProgressBar:
                id: progress_bar
                pos_hint: {"center_y": 0.5}
                size_hint_x: 1
                value: 0
                max: 100
                color: 0, 1, 0, 1
            MDFloatingActionButton:
                id: like_button
                icon: "heart-outline"
                md_bg_color: 0, 1, 0, 1
                size_hint: None, None
                size: root.width * 0.09, root.width * 0.09
                pos_hint: {"right": 1, "center_y": 0.5}
                on_release: app.on_toggle_like()
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: root.width * 0.12
        size_hint_x: None
        width: self.minimum_width
        pos_hint: {"center_x": 0.5}
        spacing: dp(5)
        padding: dp(5)
        MDFloatingActionButton:
            id: shuffle_button
            icon: "shuffle"
            md_bg_color: 0, 1, 0, 1
            size_hint: None, None
            size: root.width * 0.10, root.width * 0.10
            on_release: app.on_toggle_shuffle()
        MDFloatingActionButton:
            id: previous_button
            icon: "skip-previous"
            md_bg_color: 0, 1, 0, 1
            size_hint: None, None
            size: root.width * 0.10, root.width * 0.10
            on_release: app.on_previous()
        MDFloatingActionButton:
            id: play_pause_button
            icon: "play"
            md_bg_color: 0, 1, 0, 1
            size_hint: None, None
            size: root.width * 0.10, root.width * 0.10
            on_release: app.on_play_pause()
        MDFloatingActionButton:
            id: next_button
            icon: "skip-next"
            md_bg_color: 0, 1, 0, 1
            size_hint: None, None
            size: root.width * 0.10, root.width * 0.10
            on_release: app.on_next()
        MDFloatingActionButton:
            id: loop_button
            icon: "repeat"
            md_bg_color: 0, 1, 0, 1
            size_hint: None, None
            size: root.width * 0.10, root.width * 0.10
            on_release: app.on_toggle_loop()

Screen:
    RelativeLayout:
        id: main_layout
        PlaySongPage:
            id: play_song_page
            pos: 0, 0
        LibraryOverlay:
            id: library_overlay
            pos: -self.width, 0
'''

# -----------------------------------
# Main Application Class
# -----------------------------------
class CombinedSpotifyGUI(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.root = Builder.load_string(KV)
        # Cache library data at startup
        try:
            self.cached_playlists, self.cached_albums = get_library(sp)
        except Exception as e:
            print("Error retrieving library:", e)
            self.cached_playlists, self.cached_albums = {}, {}
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(self.update_play_song_ui, 1)
        return self.root

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 13:  # Enter key
            self.toggle_library_overlay()
        return False

    def toggle_library_overlay(self):
        overlay = self.root.ids.library_overlay
        if overlay.x < 0:
            self.populate_library_list()
            Animation.cancel_all(overlay)
            anim = Animation(x=0, duration=0.3)
            anim.start(overlay)
        else:
            Animation.cancel_all(overlay)
            anim = Animation(x=-overlay.width, duration=0.3)
            anim.start(overlay)

    def populate_library_list(self):
        lib_list = self.root.ids.library_overlay.ids.library_list
        lib_list.clear_widgets()
        header = self._create_header("Playlists")
        lib_list.add_widget(header)
        for url, name in self.cached_playlists.items():
            item = OneLineListItem(
                text=name,
                on_release=lambda inst, url=url: self.on_library_item_select(url)
            )
            lib_list.add_widget(item)
        header = self._create_header("Albums")
        lib_list.add_widget(header)
        for url, name in self.cached_albums.items():
            item = OneLineListItem(
                text=name,
                on_release=lambda inst, url=url: self.on_library_item_select(url)
            )
            item.theme_text_color = "Custom"
            item.text_color = (0, 1, 0, 1)
            lib_list.add_widget(item)

    def _create_header(self, text):
        from kivymd.uix.label import MDLabel
        return MDLabel(
            text=text,
            halign="center",
            theme_text_color="Custom",
            text_color=(0, 1, 0, 1),
            bold=True,
            size_hint_y=None,
            height=20,
            padding=(5, 5)
        )

    def on_library_item_select(self, url):
        threading.Thread(target=self._play_context_thread, args=(url,)).start()
        overlay = self.root.ids.library_overlay
        Animation.cancel_all(overlay)
        anim = Animation(x=-overlay.width, duration=0.3)
        anim.start(overlay)

    def _play_context_thread(self, url):
        try:
            result = play_context_by_url(sp, url)
        except Exception as e:
            result = f"Error: {str(e)}"
        Clock.schedule_once(lambda dt: self.show_snackbar(result), 0)

    def update_play_song_ui(self, dt):
        try:
            current = get_current_playback()
        except Exception as e:
            print(f"Error fetching playback: {e}")
            return

        psp = self.root.ids.play_song_page
        if current and current.get("item"):
            item = current["item"]
            current_track_id = item.get("id")
            if not hasattr(self, 'current_track_id') or self.current_track_id != current_track_id:
                self.current_track_id = current_track_id
                album_images = item.get("album", {}).get("images", [])
                if album_images:
                    cover_url = album_images[0]["url"]
                    psp.ids.album_cover.source = cover_url
                    psp.ids.album_cover.reload()
                else:
                    psp.ids.album_cover.source = ""
            psp.ids.song_title.text = item.get("name", "Unknown Title")
            artists = item.get("artists", [])
            psp.ids.song_artist.text = ", ".join([a["name"] for a in artists])
            duration_ms = item.get("duration_ms", 1)
            progress_ms = current.get("progress_ms", 0)
            percentage = (progress_ms / duration_ms) * 100
            psp.ids.progress_bar.value = percentage
            if current.get("is_playing"):
                psp.ids.play_pause_button.icon = "pause"
            else:
                psp.ids.play_pause_button.icon = "play"
            song_id = item.get("id")
            if song_id:
                try:
                    liked = is_track_liked(song_id)
                    psp.ids.like_button.icon = "heart" if liked else "heart-outline"
                except Exception as e:
                    print(f"Error checking liked status: {e}")
            repeat_state = current.get("repeat_state", "off")
            if repeat_state != "off":
                psp.ids.loop_button.icon = "repeat-variant"
            else:
                psp.ids.loop_button.icon = "repeat"
            shuffle_state = current.get("shuffle_state", False)
            if shuffle_state:
                psp.ids.shuffle_button.icon = "shuffle-variant"
            else:
                psp.ids.shuffle_button.icon = "shuffle"
        else:
            psp.ids.song_title.text = "No song is playing"
            psp.ids.song_artist.text = ""
            psp.ids.album_cover.source = ""
            psp.ids.progress_bar.value = 0
            psp.ids.play_pause_button.icon = "play"
            psp.ids.loop_button.icon = "repeat"
            psp.ids.shuffle_button.icon = "shuffle"

    def show_snackbar(self, message):
        Snackbar(text=message, duration=3).open()

    def on_play_pause(self):
        threading.Thread(target=self._play_pause_thread).start()

    def _play_pause_thread(self):
        try:
            toggle_playback()
        except Exception as e:
            print(f"Error toggling playback: {e}")

    def on_previous(self):
        threading.Thread(target=self._previous_thread).start()

    def _previous_thread(self):
        try:
            previous_song()
        except Exception as e:
            print(f"Error going to previous song: {e}")

    def on_next(self):
        threading.Thread(target=self._next_thread).start()

    def _next_thread(self):
        try:
            next_song()
        except Exception as e:
            print(f"Error going to next song: {e}")

    def on_toggle_like(self):
        threading.Thread(target=self._toggle_like_thread).start()

    def _toggle_like_thread(self):
        try:
            toggle_like_current_song()
        except Exception as e:
            print(f"Error toggling like status: {e}")

    def on_toggle_shuffle(self):
        threading.Thread(target=self._toggle_shuffle_thread).start()

    def _toggle_shuffle_thread(self):
        try:
            toggle_shuffle()
        except Exception as e:
            print(f"Error toggling shuffle: {e}")

    def on_toggle_loop(self):
        threading.Thread(target=self._toggle_loop_thread).start()

    def _toggle_loop_thread(self):
        try:
            toggle_loop()
        except Exception as e:
            print(f"Error toggling loop: {e}")

if __name__ == '__main__':
    CombinedSpotifyGUI().run()
