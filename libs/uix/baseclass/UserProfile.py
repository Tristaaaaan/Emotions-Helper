from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from functions.db import EmotionDatabase
from kivy.clock import Clock

# user profile update


class UserProfile(BoxLayout):

    Builder.load_file('libs/uix/kv/UserProfile.kv')

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self.profile()

    def profile(self):
        db3 = EmotionDatabase()
        user_data = db3.get_any_user_data()

        if user_data:
            id, username, location, other_info = user_data
            self.ids.txt_id.text = str(id)
            self.ids.username.text = username
            self.ids.user_location.text = f"{location}"
            self.ids.user_info.text = f"{other_info}"
        else:
            # Handle the case when there is no user data
            print("No user data found")

        # Close the database connection
        db3.close_connection()

    def call_homepage(self, args):
        self._parent.homepage()

    def update_profile(self):
        user_id = int(self.ids.txt_id.text)
        new_username = self.ids.username.text
        new_location = self.ids.user_location.text
        new_other_info = self.ids.user_info.text
        self.notify = self.ids.form_mesg
        if not new_username or not new_location or not new_other_info:
            self.notify.text = 'All fields are mandatory!'
            self.notify.color = 1, 0, 0, 1
            self.notify.bold = False
        else:
            db4 = EmotionDatabase()
            update_result = db4.update_user_by_id(
                user_id, new_username, new_location, new_other_info)
            if update_result:
                self.notify.text = 'The user details has been updated.'
                self.notify.color = 0, 0, 1, 1
                self.notify.bold = False
                self.ids.btn_update.disabled = True
                db4.close_connection()
                Clock.schedule_once(self.call_homepage, 2)
            else:
                self.notify.text = 'Oops! Something went wrong. Please try again.'
                self.notify.color = 1, 0, 0, 1
                self.notify.bold = False
                db4.close_connection()
