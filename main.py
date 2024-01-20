import kivy
from kivy.core.window import Window

from db import EmotionDatabase
from kivy.utils import platform

import time
from kivy import platform

import functools
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from textwrap import fill

import logging
import html
import json

import requests
from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.clock import mainthread

from kivy.core.window import Window


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

#Jokes
jokes_api_url = "https://v2.jokeapi.dev/joke/Any"

#News
news_api_url = "https://newsapi.org/v2/top-headlines"
news_api_key = "ffd29ba343054dd9872860c04aa76563"

#trivia
trivia_api_url = "https://opentdb.com/api.php"

# Set the logging level to WARNING
logging.basicConfig(level=logging.WARNING)

# table list
class HistoryListButton(BoxLayout, Button):
    def __init__(self, **kwargs) -> None:
        super(HistoryListButton, self).__init__()


# styled button
class StyledButton(Button):
    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.background_normal = 'button.png'
        self.background_down = 'button_p.png'


# Home page
class Homepage(BoxLayout):
    id = None
    username = None
    location = None
    other_info = None
    sentiment = 'NEUTRAL'
    isFirst = True

    def __init__(self,parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=parent
        self.user_data()
        self.populate_form()
        self.stop_recording()
        
    def user_data(self):
        self.db = EmotionDatabase()
        user_data = self.db.get_any_user_data()

        if user_data:
            #get the data from the database
            Homepage.id, Homepage.username, Homepage.location, Homepage.other_info = user_data
            #set the user name lable
            self.ids.lbl_user.text = Homepage.username
            #set the location lable
            self.ids.lbl_location.text = f"{Homepage.location}"
        else:
            print("No user data found")

        # Close the database connection
        self.db.close_connection()

    def populate_form(self):
        self.btn_box=self.ids.record_btn_area
        self.listen_button = StyledButton(text="Listen",bold=True,color=(1,1,1,1), on_press=self.on_button_press)
        self.btn_box.add_widget(self.listen_button)
        isFirst = True

    def stop_recording(self):
        self.btn_box=self.ids.record_btn_area
        self.stop_button = StyledButton(text="Stop",bold=True,color=(1,1,1,1), on_press=self.cancel_record)
        self.btn_box.add_widget(self.stop_button)

    def on_button_press(self, instance):

        self.listen_button.background_normal = 'button_p.png'

        self.ids.txt_output.text += "Listening..."

        self.ids.txt_output.text += "\nThe recording has started, you may speak now."
        
        self.speech_events = SpeechEvents()

        self.speech_events.create_recognizer(self.recognizer_event_handler)  

    
                    
        if self.speech_events:

            self.unwrapped = ''

            self.speech_events.start_listening()   
                

    def cancel_record(self, instance):
        self.speech_events.stop_listening()


        if Homepage.isFirst:

            text = self.unwrapped

            # Recognize sentiment based on the audio
            ltext = text.lower()
            if "sad" in ltext or "mad" in ltext or "bad" in ltext or "stress" in ltext or "tired" in ltext or "worried" in ltext:
                Homepage.sentiment = "NEGATIVE"
            elif "happy" in ltext or "great" in ltext or "enjoy" in ltext or "excited" in ltext or "happy" in ltext:
                Homepage.sentiment = "POSITIVE"
            else:
                Homepage.sentiment = "NEUTRAL"
            self.insert_history()

            

            self.ids.txt_output.text += f"\n\nUser Text:\n{text}\n\nDetected Sentiment: {Homepage.sentiment}"
            #self.speak_out_feedback(self.interactive_feedback(sentiment))
            # Get the current day of the week
            day_of_week = datetime.now().strftime("%A")
            self.ids.txt_output.text += f"\n\nToday is {day_of_week}."
            # Get the local weather information
            weather_info = self.get_weather_info()
            self.ids.txt_output.text += f"\n{weather_info}"
            # Generate personalized feedback using GPT-3
            personalized_feedback = self.generate_personalized_feedback(text, weather_info, day_of_week)
        else:
            
            ltext = text.lower()
            if 'motivat' in ltext:
                text = 'give me in one line an emotional motivalional quote'
                personalized_feedback = self.generate_personalized_feedback(text, '', '')
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
                personalized_feedback = self.generate_personalized_feedback(text, '', '')

        self.feedback_label.text += f"\n\nPersonalized Feedback:\n{personalized_feedback}

        # Speak out the personalized feedback

        options = self.feedback_options(Homepage.sentiment)
        combined = personalized_feedback + options
        print(combined)
        self.speak_out_feedback(combined)

        Homepage.isFirst = False
        
        self.listen_button.background_normal = 'button.png'

    @mainthread
    def recognizer_event_handler(self, key, value):
        if key == 'onReadyForSpeech':
            self.ids.txt_output.text += '\n\nStatus: Listening.'
        elif key == 'onBeginningOfSpeech':
            self.ids.txt_output.text += '\n\nStatus: Speaker Detected.'
        elif key == 'onEndOfSpeech':
            self.ids.txt_output.text += '\n\nStatus: Not Listening.'
        elif key == 'onError':
            self.ids.txt_output.text += '\n\nStatus: Currently, the Speech Recognizer is encountering an error kindly wait a little bit.'      
        elif key in ['onPartialResults', 'onResults']:
            self.unwrapped = str(value)
        elif key in ['onBufferReceived', 'onEvent', 'onRmsChanged']:
            pass


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
            'q': Homepage.location,
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
        params = {"amount": 1, "category": category, "difficulty": difficulty, "type": question_type,}
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
            print(f"Failed to fetch trivia question. Status code: {response.status_code}")
        return rval
    
    def get_joke(self):
        params = {"format": "json", "type": "twopart", "lang": "en", "category": "programming", "safe-mode":""}
        response = requests.get(jokes_api_url, params=params, headers={"Accept": "application/json"})
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
        params = {"country": country, "category": category, "pageSize": page_size, "apiKey": news_api_key,}
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

    # def recognize_sentiment(self, audio_data):
    #     sentiment_classifier = pipeline("sentiment-analysis")
    #     result = sentiment_classifier(audio_data)[0]
    #     sentiment_label = result['label']
    #     return sentiment_label

    # def interactive_feedback(self, sentiment):
    #     if sentiment == 'POSITIVE':
    #         feedback = "Great job! Keep up the positive vibes!"
    #     elif sentiment == 'NEGATIVE':
    #         feedback = "I'm here for you. If you want to talk or need support, I'm just a message away."
    #     else:
    #         feedback = "Neutral feelings are okay too. Is there anything specific on your mind?"

    #     return feedback

    def feedback_options(self, sentiment):
        if sentiment == 'POSITIVE':
            if isFirst:
                feedback = "Would you like me to share knowledge about any topic?"
            else:
                feedback = "Would you like to know about anything else?"
        elif sentiment == 'NEGATIVE':
            if isFirst:
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
        if (isFirst):
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
            #response_data = json.loads(result)

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
            #generated_text = result['choices'][0]['text']
            return content
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None

    def speak_out_feedback(self, feedback):
        tts.setLanguage(Locale.US)
        tts.speak(feedback, TextToSpeech.QUEUE_FLUSH, None)

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()


# user profile update  
class UserProfile(BoxLayout):
    def __init__(self,parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=parent
        self.profile()

    def profile(self):
        self.db = TestDatabase()
        user_data = self.db.get_any_user_data()

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
        self.db.close_connection()

    def call_homepage(self,args):
        self._parent.homepage()
        
    def update_profile(self):
        user_id = int(self.ids.txt_id.text)
        new_username = self.ids.username.text
        new_location = self.ids.user_location.text
        new_other_info = self.ids.user_info.text
        self.notify = self.ids.form_mesg
        if not new_username or not new_location or not new_other_info:
            self.notify.text='All fields are mandatory!'
            self.notify.color=1,0,0,1
            self.notify.bold=False
        else:
            self.db = TestDatabase()
            update_result = self.db.update_user_by_id(user_id, new_username, new_location, new_other_info)
            if update_result:
                self.notify.text='Profile Updated!'
                self.notify.color=0,1,0,1
                self.notify.bold=False
                self.ids.btn_update.disabled = True
                self.db.close_connection()
                Clock.schedule_once(self.call_homepage, 2)
            else:
                self.notify.text='Something went Wrong!'
                self.notify.color=1,0,0,1
                self.notify.bold=False
                self.db.close_connection()


# User Register Page
class UserRegister(BoxLayout):
    def __init__(self,parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=parent

    def call_homepage(self,args):
        self._parent.homepage()

    def register(self):
        username = self.ids.username.text
        location = self.ids.user_location.text
        other_info = self.ids.user_info.text
        self.notify = self.ids.form_mesg
        if not username or not location or not other_info:
            self.notify.text='All fields are mandatory!'
            self.notify.color=1,0,0,1
            self.notify.bold=False

        else:
            self.db = TestDatabase()
            save_record = self.db.insert_user_data(username, location, other_info)
            if save_record:
                self.notify.text='User Details are saved!'
                self.notify.color=0,0,1,1
                self.notify.bold=False
                self.ids.btn_register.disabled = True
                self.db.close_connection()
                Clock.schedule_once(self.call_homepage, 2)
            else:
                self.notify.text='Something went Wrong!'
                self.notify.color=1,0,0,1
                self.notify.bold=False
                self.db.close_connection()


# user history
class History(BoxLayout):
    def __init__(self,parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=parent
        self.load_list()

    def load_list(self):
        table_box=self.ids.row_task_box
        table_box.clear_widgets()
        self.db = TestDatabase()
        results = self.db.get_history()
        if results:
            for i, result in enumerate(results):
                row=HistoryListButton()
                id=result[0]
                date=result[1]
                row.ids.lbl_date.text=date
                row.ids.lbl_value1.text=result[2]
                row.ids.lbl_value2.text=result[3]
                row.ids.lbl_value3.text=result[4]
                # row.bind(on_press=partial(self._parent.call_task_page, id))
                table_box.add_widget(row)


# main app
class Main(BoxLayout):

    def __init__(self,**kwargs):
        super(Main, self).__init__(**kwargs)
        self.dynamic_area=self.ids.dynamic_box
        self.validate()

    def validate(self):
        self.home_page = Homepage(self)
        self.user_register = UserRegister(self)
        self.dynamic_area.clear_widgets()
        self.db = TestDatabase()
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
class MainApp(App):
    def build(self):
        return Main()

if __name__=="__main__":
    pa=MainApp()
    pa.run()

