# Set the window size to simulate a 320 x 480 display
from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation

class SpotifyController(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set overall layout properties
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # Title Label
        title = Label(text="My Spotify Controller",
                      font_size="24sp",
                      size_hint=(1, 0.2))
        self.add_widget(title)

        # Create two rows for control buttons
        btn_row1 = BoxLayout(orientation="horizontal",
                             spacing=10,
                             size_hint=(1, 0.2))
        btn_row2 = BoxLayout(orientation="horizontal",
                             spacing=10,
                             size_hint=(1, 0.2))

        # Create control buttons with vibrant background colors
        play_btn = Button(text="Play", background_color=(0.1, 0.8, 0.1, 1))
        pause_btn = Button(text="Pause", background_color=(0.8, 0.1, 0.1, 1))
        prev_btn = Button(text="Previous", background_color=(0.1, 0.1, 0.8, 1))
        next_btn = Button(text="Next", background_color=(0.8, 0.8, 0.1, 1))

        # Bind button press events to the animate_button function
        play_btn.bind(on_press=self.animate_button)
        pause_btn.bind(on_press=self.animate_button)
        prev_btn.bind(on_press=self.animate_button)
        next_btn.bind(on_press=self.animate_button)

        # Add buttons to rows
        btn_row1.add_widget(play_btn)
        btn_row1.add_widget(pause_btn)
        btn_row2.add_widget(prev_btn)
        btn_row2.add_widget(next_btn)

        # Add button rows to main layout
        self.add_widget(btn_row1)
        self.add_widget(btn_row2)

        # (Optional) Additional space or UI elements can be added here

    def animate_button(self, instance):
        """Animate a button by briefly enlarging it then returning to its original size."""
        original_size = instance.size

        # Create an animation: enlarge by 10% and then revert
        anim = Animation(size=(original_size[0] * 1.1, original_size[1] * 1.1), duration=0.1) + \
               Animation(size=original_size, duration=0.1)
        anim.start(instance)

        # For now, just print which button was pressed.
        print(f"{instance.text} button pressed!")

class SpotifyApp(App):
    def build(self):
        return SpotifyController()

if __name__ == '__main__':
    SpotifyApp().run()
