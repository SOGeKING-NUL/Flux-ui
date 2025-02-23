#!/usr/bin/env python3
import threading
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.snackbar import Snackbar

from spotify_controller import get_library, play_context_by_url, sp

Window.size = (240, 320)

KV = '''
Screen:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(5)
        spacing: dp(5)
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
'''

class LibraryGUI(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        return Builder.load_string(KV)

    def on_start(self):
        try:
            playlists, albums = get_library(sp)
        except Exception as e:
            self.show_snackbar(f"Library Error: {str(e)}")
            return

        library_list = self.root.ids.library_list

        library_list.add_widget(self._create_header("Playlists"))
        for url, name in playlists.items():
            item = OneLineListItem(
                text=name,
                on_release=lambda inst, url=url: self.play_context(url)
            )
            library_list.add_widget(item)

        library_list.add_widget(self._create_header("Albums"))
        for url, name in albums.items():
            item = OneLineListItem(
                text=name,
                on_release=lambda inst, url=url: self.play_context(url)
            )
            item.theme_text_color = "Custom"
            item.text_color = (0, 1, 0, 1)
            library_list.add_widget(item)

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

    def play_context(self, url):
        threading.Thread(
            target=self._play_context_thread,
            args=(url,),
            daemon=True
        ).start()

    def _play_context_thread(self, url):
        try:
            result = play_context_by_url(sp, url)
        except Exception as e:
            result = f"Error: {str(e)}"
        finally:
            Clock.schedule_once(lambda dt: self.show_snackbar(result), 0)

    def show_snackbar(self, message):
        Snackbar(text=message, duration=3).open()

if __name__ == "__main__":
    LibraryGUI().run()
