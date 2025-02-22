import RPi.GPIO as GPIO
from kivy.clock import Clock

# Define GPIO pins
UP_BUTTON = 17
DOWN_BUTTON = 27
SELECT_BUTTON = 22

class GPIOHandler:
    def __init__(self, app):
        self.app = app
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(UP_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DOWN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(SELECT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection for buttons
        GPIO.add_event_detect(UP_BUTTON, GPIO.FALLING, callback=self.on_up_press, bouncetime=200)
        GPIO.add_event_detect(DOWN_BUTTON, GPIO.FALLING, callback=self.on_down_press, bouncetime=200)
        GPIO.add_event_detect(SELECT_BUTTON, GPIO.FALLING, callback=self.on_select_press, bouncetime=200)

    def on_up_press(self, channel):
        Clock.schedule_once(lambda dt: self.app.navigate("up"), 0)

    def on_down_press(self, channel):
        Clock.schedule_once(lambda dt: self.app.navigate("down"), 0)

    def on_select_press(self, channel):
        Clock.schedule_once(lambda dt: self.app.select_option(), 0)

    def cleanup(self):
        """Cleanup GPIO on app exit."""
        GPIO.cleanup()
