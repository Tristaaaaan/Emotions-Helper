import kivy
from kivy.core.window import Window

from db import EmotionDatabase
from kivy.utils import platform
from kivymd.uix.button import MDFlatButton
import time
from kivy import platform
from kivy.uix.screenmanager import ScreenManager, Screen
import functools
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from textwrap import fill
from kivymd.app import MDApp
import logging
import html
import json

import requests
from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.clock import mainthread
import threading
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

if platform == "android":
    from speech_events import SpeechEvents
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    # Define the required permissions
    request_permissions([
        Permission.RECORD_AUDIO,
        Permission.INTERNET
    ])

    Locale = autoclass('java.util.Locale')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    tts = TextToSpeech(PythonActivity.mActivity, None)

# Set your GPT-3 API key here
openai_api_url = 'https://api.openai.com/v1/chat/completions'

openai_api_key = "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"

# Set your OpenWeatherMap API key here
weather_api_key = "998ca18b83bdd1414d79ce4f77c30de1"
weather_api_url = "http://api.openweathermap.org/data/2.5/weather"

# Jokes
jokes_api_url = "https://v2.jokeapi.dev/joke/Any"

# News
news_api_url = "https://newsapi.org/v2/top-headlines"
news_api_key = "ffd29ba343054dd9872860c04aa76563"

# trivia
trivia_api_url = "https://opentdb.com/api.php"

# Set the logging level to WARNING
logging.basicConfig(level=logging.WARNING)

# table list


class HistoryListButton(BoxLayout, Button):
    def __init__(self, **kwargs) -> None:
        super(HistoryListButton, self).__init__()


# Home page
class Homepage(Screen):
    id = None
    username = None
    location = None
    other_info = None
    sentiment = 'NEUTRAL'
    isFirst = True

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self.user_data()
        self.populate_form()

    def user_data(self):
        self.db = EmotionDatabase()
        user_data = self.db.get_any_user_data()

        if user_data:
            # get the data from the database
            Homepage.id, Homepage.username, Homepage.location, Homepage.other_info = user_data
            # set the user name lable
            self.ids.lbl_user.text = f"Good day, {Homepage.username}!"
            # set the location lable
            self.ids.lbl_location.text = f"{Homepage.location}"
        else:
            print("No user data found")

        # Close the database connection
        self.db.close_connection()

    def populate_form(self):
        # self.speak_out_feedback("Hello, how are you doing today?")
        Homepage.isFirst = True

    def start_recording(self):

        if self.ids.btn_record.text == 'Record':

            self.ids.txt_output.text = ''

            self.ids.txt_output.text += "\nThe recording has started, you may speak now."

            self.ids.btn_record.md_bg_color = [
                239/255, 153/255, 117/255, 1]

            self.ids.btn_record.text = 'Stop Recording'

            self.ids.btn_record.text_color = 'white'

            # UNCOMMENT - for Speech to Text

            # self.speech_events = SpeechEvents()

            # self.speech_events.create_recognizer(self.recognizer_event_handler)

            # if self.speech_events:

            #     self.unwrapped = ''

            #     self.speech_events.start_listening()

        else:

            self.ids.btn_record.md_bg_color = [
                0, 152/255, 153/255, 1]

            self.ids.btn_record.text = 'Record'

            self.ids.btn_record.text_color = 'white'

            process = threading.Thread(target=self.process_recorded_text)
            process.start()

    def process_recorded_text(self):

        # UNCOMMENT - for Speech to Text

        # self.speech_events.stop_listening()

        text = 'I am so happy!'  # self.unwrapped

        if Homepage.isFirst:

            # Recognize sentiment based on the audio
            ltext = text.lower()
            if "sad" in ltext or "mad" in ltext or "bad" in ltext or "stress" in ltext or "tired" in ltext or "worried" in ltext:
                Homepage.sentiment = "NEGATIVE"
            elif "happy" in ltext or "great" in ltext or "enjoy" in ltext or "excited" in ltext or "happy" in ltext:
                Homepage.sentiment = "POSITIVE"
            else:
                Homepage.sentiment = "NEUTRAL"
            self.insert_history()

            self.ids.txt_output.text += f"\n\nUser Text: {text}\n\nDetected Sentiment: {Homepage.sentiment}"

            # self.speak_out_feedback(self.interactive_feedback(sentiment))

            # Get the current day of the week
            day_of_week = datetime.now().strftime("%A")
            self.ids.txt_output.text += f"\n\nToday is {day_of_week}."

            # Get the local weather information
            weather_info = self.get_weather_info()
            self.ids.txt_output.text += f"\n{weather_info}"

            # Generate personalized feedback using GPT-3
            personalized_feedback = self.generate_personalized_feedback(
                text, weather_info, day_of_week)
        else:

            ltext = text.lower()

            if 'motivat' in ltext:
                text = 'give me in one line an emotional motivalional quote'
                personalized_feedback = self.generate_personalized_feedback(
                    text, '', '')
            elif 'joke' in ltext:
                personalized_feedback = self.get_joke()
            elif 'news' in ltext:
                personalized_feedback = self.get_news()
            elif 'weather' in ltext:
                personalized_feedback = self.get_weather_info()
            elif 'trivia' in ltext:
                personalized_feedback = self.get_trivia()
            else:
                text = f"give me in one or two lines for {text}"
                personalized_feedback = self.generate_personalized_feedback(
                    text, '', '')

        self.ids.txt_output.text += f"\n\nPersonalized Feedback:\n{personalized_feedback}"

        # Speak out the personalized feedback

        options = self.feedback_options(Homepage.sentiment)
        combined = str(personalized_feedback) + options
        print(combined)

        # UNCOMMENT - for Text to Speech

        # self.speak_out_feedback(combined)

        Homepage.isFirst = False

    # UNCOMMENT - for Speech to Text

    # @mainthread
    # def recognizer_event_handler(self, key, value):
    #     if key == 'onReadyForSpeech':
    #         self.ids.txt_output.text += '\n\nStatus: Listening.'
    #     elif key == 'onBeginningOfSpeech':
    #         self.ids.txt_output.text += '\n\nStatus: Speaker Detected.'
    #     elif key == 'onEndOfSpeech':
    #         self.ids.txt_output.text += '\n\nStatus: Not Listening.'
    #     elif key == 'onError':
    #         self.ids.txt_output.text += '\n\nStatus: Currently, the Speech Recognizer is encountering an error kindly wait a little bit.'
    #     elif key in ['onPartialResults', 'onResults']:
    #         self.unwrapped = str(value)
    #     elif key in ['onBufferReceived', 'onEvent', 'onRmsChanged']:
    #         pass

    def insert_history(self):
        try:
            self.db = EmotionDatabase()
            self.db.insert_history_entry(Homepage.sentiment)
            self.db.close_connection()
        except Exception as e:
            print(e)
            self.db.close_connection()

    def get_weather_info(self):
        params = {
            'q': 'Atlanta,GA,USA',  # Homepage.location,
            'appid': weather_api_key,
            'units': 'imperial'  # You can change this to 'imperial' for Fahrenheit
        }

        response = requests.get(weather_api_url, params=params)
        data = response.json()
        print('weather data')
        print(data)

        if response.status_code == 200:
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            return f"The weather in {Homepage.location} is {weather_description}. The current temperature is {temperature}°F."

        return ""

    def get_trivia(self, category="9", difficulty="medium", question_type="multiple"):
        params = {"amount": 1, "category": category,
                  "difficulty": difficulty, "type": question_type, }
        response = requests.get(trivia_api_url, params=params)
        rval = ''
        if response.status_code == 200:
            trivia_data = response.json()
            question = trivia_data.get("results", [])[0]
            decoded_question = html.unescape(question["question"])
            rval += f"Question: {decoded_question}"
            rval += "  \n\n"
            rval += "The options are: \n"
            rval += f"A - {html.unescape(question['correct_answer'])}"
            rval += "  \n"
            rval += f"B - {html.unescape(question['incorrect_answers'][0])}"
            rval += "  \n"
            rval += f"C - {html.unescape(question['incorrect_answers'][1])}"
            rval += "  \n"
            rval += f"D - {html.unescape(question['incorrect_answers'][2])}"
            rval += "  \n"
            rval += "     \n"
            rval += f"The Correct Answer is: {html.unescape(question['correct_answer'])}"
        else:
            print(
                f"Failed to fetch trivia question. Status code: {response.status_code}")
        return rval

    def get_joke(self):
        params = {"format": "json", "type": "twopart", "lang": "en",
                  "category": "programming", "safe-mode": ""}
        response = requests.get(jokes_api_url, params=params, headers={
                                "Accept": "application/json"})
        if response.status_code == 200:
            joke_data = response.json()
            rval = ''
            if joke_data["type"] == "twopart":
                setup, delivery = joke_data["setup"], joke_data["delivery"]
                rval += f"{setup}\n\n{delivery}\n"
            else:
                rval += f"{joke_data['joke']}\n\n"
            rval += "Hope that made you laugh."
        else:
            print(f"Failed to fetch joke. Status code: {response.status_code}")
        return rval

    def get_news(self, country="us", category="general", page_size=2):
        params = {"country": country, "category": category,
                  "pageSize": page_size, "apiKey": news_api_key, }
        rval = ''
        response = requests.get(news_api_url, params=params)
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get("articles", [])
            rval += "The News is \n"
            for i, article in enumerate(articles, start=1):
                rval += f"{article['title']}\n\n"
        else:
            print(f"Failed to fetch news. Status code: {response.status_code}")
        return rval

    def feedback_options(self, sentiment):
        if sentiment == 'POSITIVE':
            if Homepage.isFirst:
                feedback = "Would you like me to share knowledge about any topic?"
            else:
                feedback = "Would you like to know about anything else?"
        elif sentiment == 'NEGATIVE':
            if Homepage.isFirst:
                feedback = "Would you like to hear a joke or a motivational quote?"
            else:
                feedback = "Would you like to know about anything else?"
        else:
            feedback = "Neutral feelings are okay too. Is there anything specific on your mind?"

        return feedback

    def generate_personalized_feedback(self, text, weathertx,  day_of_week):

        # Use GPT-3 to generate personalized feedback
        userid = 'Saanvi'
        initial_prompt = f"user name={userid}, today is {day_of_week}, my weather is {weathertx}"
        if (Homepage.isFirst):
            prompt = f"Generate personalized feedback for the user's emotional feeling: {initial_prompt}, I feel {text}"
        else:
            prompt = f"Generate personalized feedback {text}"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_api_key}'
        }

        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            'model': 'gpt-3.5-turbo',
        }

        response = requests.post(openai_api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            # Parse the JSON response
            # response_data = json.loads(result)

            # Extract content from the "choices" array
            choices = result.get("choices", [])
            if choices:
                first_choice = choices[0]
                message = first_choice.get("message", {})
                content = message.get("content", "")

                # Print or use the content
                print("Content:", content)

                return content

            else:
                print("No choices in the response.")
            # generated_text = result['choices'][0]['text']
            return content
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None

    def speak_out_feedback(self, feedback):
        tts.setLanguage(Locale.US)
        tts.speak(feedback, TextToSpeech.QUEUE_FLUSH, None)

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content),
                      size_hint=(None, None), size=(400, 200))
        popup.open()


# user profile update
class UserProfile(Screen):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self.profile()

    def profile(self):
        self.db = EmotionDatabase()
        user_data = self.db.get_any_user_data()

        if user_data:
            id, username, location, other_info = user_data
            self.id = id
            self.ids.username.text = username
            self.ids.user_location.text = f"{location}"
            self.ids.user_info.text = f"{other_info}"
        else:
            # Handle the case when there is no user data
            print("No user data found")

        # Close the database connection
        self.db.close_connection()

    def call_homepage(self, args):
        self.dialog.dismiss()
        self._parent.homepage()

    def back_to_home(self, args):
        self._parent.homepage()

    def update_profile(self):
        user_id = self.id
        new_username = self.ids.username.text
        new_location = self.ids.user_location.text
        new_other_info = self.ids.user_info.text
        if not new_username or not new_location or not new_other_info:
            message = 'Make sure to fill up all the required information to proceed.'
            self.error_dialog(message)
        else:
            self.db = EmotionDatabase()
            update_result = self.db.update_user_by_id(
                user_id, new_username, new_location, new_other_info)
            if update_result:
                message = 'Your profile has been updated.'
                self.save_dialog(message)
                self.db.close_connection()
                Clock.schedule_once(self.call_homepage, 2)
            else:
                self.notify.text = 'There was an error, please try again.'
                self.error_dialog(message)
                self.db.close_connection()

    def error_dialog(self, message):

        close_button = MDFlatButton(
            text='CLOSE',
            text_color=[0, 0, 0, 1],
            on_release=self.close_dialog,
        )
        self.dialog = MDDialog(
            title='[color=#FF0000]Ooops![/color]',
            text=message,
            buttons=[close_button],
        )
        self.dialog.open()

    def save_dialog(self, message):

        close_button = MDFlatButton(
            text='CLOSE',
            text_color=[0, 0, 0, 1],
            on_release=self.close_dialog,
        )
        self.dialog = MDDialog(
            title='[color=#65C0e5]Success[/color]',
            text=message,
            buttons=[close_button],
        )
        self.dialog.open()

    # Close Dialog
    def close_dialog(self, obj):
        self.dialog.dismiss()

# User Register Page


class UserRegister(Screen):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent

    def call_homepage(self, args):
        self._parent.homepage()

    def register(self):
        username = self.ids.username.text
        location = self.ids.user_location.text
        other_info = self.ids.user_info.text

        if not username or not location or not other_info:
            message = 'Make sure to fill up all the required information to proceed.'
            self.error_dialog(message)

        else:
            self.db = EmotionDatabase()
            save_record = self.db.insert_user_data(
                username, location, other_info)
            if save_record:
                self.db.close_connection()
                Clock.schedule_once(self.call_homepage, 2)
            else:
                self.notify.text = 'There was an error, please try again.'
                self.error_dialog(message)
                self.db.close_connection()

    def error_dialog(self, message):

        close_button = MDFlatButton(
            text='CLOSE',
            text_color=[0, 0, 0, 1],
            on_release=self.close_dialog,
        )
        self.dialog = MDDialog(
            title='[color=#FF0000]Ooops![/color]',
            text=message,
            buttons=[close_button],
        )
        self.dialog.open()

    # Close Dialog
    def close_dialog(self, obj):
        self.dialog.dismiss()

# user history


class History(Screen):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self.load_list()

    def load_list(self):
        table_box = self.ids.row_task_box
        table_box.clear_widgets()
        self.db = EmotionDatabase()
        results = self.db.get_history()
        if results:
            for i, result in enumerate(results):
                row = HistoryListButton()
                id = result[0]
                date = result[1]
                row.ids.lbl_date.text = date
                row.ids.lbl_value1.text = result[2]
               # row.ids.lbl_value2.text = result[3]
                # row.ids.lbl_value3.text = result[4]
                # row.bind(on_press=partial(self._parent.call_task_page, id))
                table_box.add_widget(row)


# main app
class Main(BoxLayout):

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.dynamic_area = self.ids.dynamic_box
        self.validate()

    def validate(self):
        self.home_page = Homepage(self)
        self.user_register = UserRegister(self)
        self.dynamic_area.clear_widgets()
        self.db = EmotionDatabase()
        user_data = self.db.get_any_user_data()

        if user_data:
            print('something i found')
            self.dynamic_area.add_widget(self.home_page)

        else:
            print('not found anything')
            self.dynamic_area.clear_widgets()
            self.dynamic_area.add_widget(self.user_register)

        self.db.close_connection()

    def homepage(self):
        self.home_page = Homepage(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.home_page)

    def profile(self):
        self.profile_page = UserProfile(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.profile_page)

    def history(self):
        self.history_page = History(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.history_page)

# build & run application


class MainApp(MDApp):
    def build(self):
        return Main()


if __name__ == "__main__":
    pa = MainApp()
    pa.run()
