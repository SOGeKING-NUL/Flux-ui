# screens/home.py
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from gpio.input_handler import InputHandler

class HomeScreen(Screen):
    title = StringProperty("Flux3.14")  # Default title
    menu_options = ListProperty([
        "Artists",
        "Albums",
        "New Releases",
        "Playlists",
        "Search"
    ])
    selected_index = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_handler = InputHandler(self.navigate, self.select)
        
    def navigate(self, direction):
        if direction == "up":
            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
        elif direction == "down":
            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
        self.title = self.menu_options[self.selected_index]  # Update title bar dynamically
        self.update_display()

    def select(self):
        selected_option = self.menu_options[self.selected_index]
        self.manager.current = selected_option.lower().replace(" ", "_")

    def update_display(self):
        self.ids.menu_list.refresh_from_data()
