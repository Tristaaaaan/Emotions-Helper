from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from functions.db import EmotionDatabase
from kivy.clock import Clock

# User Register Page


class UserRegister(BoxLayout):

    Builder.load_file('libs/uix/kv/UserRegister.kv')

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent

    def call_homepage(self, args):
        self._parent.homepage()

    def register(self):
        username = self.ids.username.text
        location = self.ids.user_location.text
        other_info = self.ids.user_info.text
        self.notify = self.ids.form_mesg
        if not username or not location or not other_info:
            self.notify.text = 'To proceed, kindly fill in all the information.'
            self.notify.color = 1, 0, 0, 1
            self.notify.bold = False

        else:
            db = EmotionDatabase()
            save_record = db.insert_user_data(username, location, other_info)
            if save_record:
                self.notify.text = 'The user details has been saved.'
                self.notify.color = 0, 0, 1, 1
                self.notify.bold = False
                self.ids.btn_register.disabled = True
                db.close_connection()
                Clock.schedule_once(self.call_homepage, 2)
            else:
                self.notify.text = 'Oops! Something went wrong. Please try again.'
                self.notify.color = 1, 0, 0, 1
                self.notify.bold = False
                db.close_connection()
