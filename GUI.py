#!/usr/bin/env python3
import threading
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ListProperty

from kivymd.app import MDApp

# Set the initial window size to 240x320px
Window.size = (240, 320)
# Set the window background color to black
Window.clearcolor = (0, 0, 0, 1)

# Import your Spotipy functions from your separate file (adjust the module name as needed)
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

# -----------------------------------
# New MarqueeLabel Implementation
# -----------------------------------
class MarqueeLabel(RelativeLayout):
    text = StringProperty("")
    font_size = NumericProperty("20sp")
    text_color = ListProperty([0, 1, 0, 1])
    delay = NumericProperty(2)  # seconds before starting marquee
    speed = NumericProperty(30) # pixels per second

    def __init__(self, **kwargs):
        super(MarqueeLabel, self).__init__(**kwargs)
        # Create an inner label; we set size_hint to None so we can control its width.
        self.label = Label(text=self.text,
                           font_size=self.font_size,
                           color=self.text_color,
                           size_hint=(None, None))
        self.add_widget(self.label)
        self.bind(text=self._update_label,
                  font_size=self._update_label,
                  text_color=self._update_label,
                  size=self._update_label)
        # Delay starting the marquee until after self.delay seconds.
        Clock.schedule_once(self._start_marquee, self.delay)

    def _update_label(self, *args):
        self.label.text = self.text
        self.label.font_size = self.font_size
        self.label.color = self.text_color
        self.label.texture_update()
        # Set the label's width to the texture width and height to the container height.
        self.label.width = self.label.texture_size[0]
        self.label.height = self.height
        # Initially position the label off to the right.
        self.label.x = self.width
        # Restart marquee scheduling
        Clock.unschedule(self._marquee_update)
        if self.label.width > self.width:
            Clock.schedule_interval(self._marquee_update, 1/30.0)
        else:
            # Center the text if no marquee is needed.
            self.label.x = (self.width - self.label.width) / 2

    def on_size(self, *args):
        self._update_label()

    def _start_marquee(self, dt):
        if self.label.width > self.width:
            Clock.schedule_interval(self._marquee_update, 1/30.0)

    def _marquee_update(self, dt):
        # Move label left by speed * dt pixels.
        self.label.x -= self.speed * dt
        # If the label has completely scrolled out, reset it.
        if self.label.x < -self.label.width:
            self.label.x = self.width

# -----------------------------------
# KV Layout String
# -----------------------------------
KV = '''
#:import dp kivy.metrics.dp
Screen:
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(5)
        
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: 0.8
            spacing: dp(5)
            
            # Album Cover (centered, dynamic size, rounded edges)
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
                    
            # Marquee for Song Title (if too long, slides right to left)
            MarqueeLabel:
                id: song_title
                text: "Song Title"
                font_size: "18sp"
                size_hint_y: None
                height: dp(25)
            # Marquee for Artist Name
            MarqueeLabel:
                id: song_artist
                text: "Artist"
                font_size: "14sp"
                size_hint_y: None
                height: dp(20)
                
            # Relative layout for progress bar with like button overlay
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
        
        # Controls Layout (single row with shuffle, previous, play/pause, next, loop)
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
'''

# -----------------------------------
# Main Application Class
# -----------------------------------
class SpotifyGUI(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.root = Builder.load_string(KV)
        # Schedule UI update every second
        Clock.schedule_interval(self.update_ui, 1)
        return self.root

    def update_ui(self, dt):
        try:
            current = get_current_playback()
        except Exception as e:
            print(f"Error fetching playback: {e}")
            return

        if current and current.get("item"):
            item = current["item"]
            current_track_id = item.get("id")

            # Update album cover only if the track has changed
            if not hasattr(self, 'current_track_id') or self.current_track_id != current_track_id:
                self.current_track_id = current_track_id
                album_images = item.get("album", {}).get("images", [])
                if album_images:
                    cover_url = album_images[0]["url"]
                    self.root.ids.album_cover.source = cover_url
                    self.root.ids.album_cover.reload()
                else:
                    self.root.ids.album_cover.source = ""

            # Update marquee texts for song title and artist
            self.root.ids.song_title.text = item.get("name", "Unknown Title")
            artists = item.get("artists", [])
            self.root.ids.song_artist.text = ", ".join([a["name"] for a in artists])

            # Update progress bar
            duration_ms = item.get("duration_ms", 1)
            progress_ms = current.get("progress_ms", 0)
            percentage = (progress_ms / duration_ms) * 100
            self.root.ids.progress_bar.value = percentage

            # Update play/pause button icon
            if current.get("is_playing"):
                self.root.ids.play_pause_button.icon = "pause"
            else:
                self.root.ids.play_pause_button.icon = "play"

            # Update like button icon based on saved status
            song_id = item.get("id")
            if song_id:
                try:
                    liked = is_track_liked(song_id)
                    self.root.ids.like_button.icon = "heart" if liked else "heart-outline"
                except Exception as e:
                    print(f"Error checking liked status: {e}")

            # Update loop button icon based on repeat state
            repeat_state = current.get("repeat_state", "off")
            if repeat_state != "off":
                self.root.ids.loop_button.icon = "repeat-variant"
            else:
                self.root.ids.loop_button.icon = "repeat"

            # Update shuffle button icon based on shuffle state
            shuffle_state = current.get("shuffle_state", False)
            if shuffle_state:
                self.root.ids.shuffle_button.icon = "shuffle-variant"
            else:
                self.root.ids.shuffle_button.icon = "shuffle"
        else:
            self.root.ids.song_title.text = "No song is playing"
            self.root.ids.song_artist.text = ""
            self.root.ids.album_cover.source = ""
            self.root.ids.progress_bar.value = 0
            self.root.ids.play_pause_button.icon = "play"
            self.root.ids.loop_button.icon = "repeat"
            self.root.ids.shuffle_button.icon = "shuffle"

    # Button action callbacks using threads
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
    SpotifyGUI().run()
