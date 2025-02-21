from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 20

    MDLabel:
        text: "Now Playing"
        halign: "center"
        font_style: "H5"

    Image:
        source: "album_art.png"
        size_hint: None, None
        size: 200, 200
        pos_hint: {"center_x": 0.5}

    BoxLayout:
        spacing: 10
        MDFloatingActionButton:
            icon: "skip-previous"
            elevation_normal: 0
            on_release: app.previous_track()

        MDFloatingActionButton:
            icon: "play"
            elevation_normal: 0
            on_release: app.play_pause()

        MDFloatingActionButton:
            icon: "skip-next"
            elevation_normal: 0
            on_release: app.next_track()
'''

class SpotifyWalkmanApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def play_pause(self):
        print("Play/Pause button pressed")

    def next_track(self):
        print("Next track button pressed")

    def previous_track(self):
        print("Previous track button pressed")

SpotifyWalkmanApp().run()

