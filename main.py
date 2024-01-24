from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from functions.db import EmotionDatabase
from kivy.utils import platform
from libs.uix.baseclass.Homepage import Homepage
from libs.uix.baseclass.UserProfile import UserProfile
from libs.uix.baseclass.History import History
from libs.uix.baseclass.UserRegister import UserRegister
import logging

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

if platform == 'win':
    Window.size = (370, 600)

if platform == 'android':
    from android.permissions import request_permissions, Permission

    # Define the required permissions
    request_permissions([
        Permission.RECORD_AUDIO,
        Permission.INTERNET
    ])


logging.getLogger("comtypes").setLevel(logging.WARNING)

# Main App

######################## main app ###############################################
#################################################################################


class Main(BoxLayout):

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.dynamic_area = self.ids.dynamic_box
        self.validate()

    # Checks if the user information is already populated. If its not, it will popup the User Registration page.
    # If the user information is already available, it will show the home screen.
    def validate(self):
        self.dynamic_area.clear_widgets()
        # Check the DB to see if the user info is there.
        db = EmotionDatabase()
        user_data = db.get_any_user_data()
        # User info is there. Show the home screen.
        if user_data:
            self.home_page = Homepage(self)
            self.dynamic_area.add_widget(self.home_page)
        # User information is not there. Show the registration screen.
        else:
            self.user_register = UserRegister(self)
            self.dynamic_area.add_widget(self.user_register)
        # Close the DB connection.
        db.close_connection()

    # Main Home Screen

    def homepage(self):
        self.home_page = Homepage(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.home_page)

    # Update Profile Screen
    def profile(self):
        self.profile_page = UserProfile(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.profile_page)

    # History Screen
    def history(self):
        self.history_page = History(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.history_page)

# Build & Run Application


class MainApp(App):
    def build(self):
        return Main()


if __name__ == "__main__":
    pa = MainApp()
    pa.run()
