from functions.integrations import AllIntegrations
from kivy.uix.boxlayout import BoxLayout
from functions.db import EmotionDatabase
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import mainthread
import threading
import time
from datetime import datetime
from kivy.app import App
from kivy.uix.popup import Popup
from functions.stt_handler import STTHandler
from functions.tts_handler import TTSHandler
# Home Page


class Homepage(BoxLayout):
    id = None
    username = None
    location = None
    other_info = None
    sentiment = 'NEUTRAL'
    isFirst = True
    helloisFirst = True
    integration = AllIntegrations()

    Builder.load_file('libs/uix/kv/HomePage.kv')

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self.user_data()
        # Check if isFirst is True before starting the thread
        if Homepage.isFirst:
            hehe = threading.Thread(target=self.populate_form)
            hehe.start()

    def user_data(self):
        db1 = EmotionDatabase()
        user_data = db1.get_any_user_data()

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
        db1.close_connection()

    def populate_form(self):

        if not Homepage.helloisFirst:  # Check if isFirst is already False
            return

        Homepage.helloisFirst = False  # Set isFirst to False to prevent further calls

        self.speak_out_feedback("HELLO <br> how are you doing today?")

    def start_recording(self):

        thread_content = threading.Thread(target=self.content_process)

        thread_content.start()

    def content_process(self):

        self.ids.btn_record.disabled = True

        self.ids.txt_output.text = ''

        self.ids.btn_history.disabled = True

        self.ids.btn_user.disabled = True

        self.ids.txt_output.text += "\nThe recording has started, you may speak now."

        # Creating an instance of STTHandler with a callback
        stt_handler_instance = STTHandler(callback=self.enable_buttons)

        # Calling getAudioText method on the same instance
        stt_handler_instance.getAudioText()

        self.ids.btn_record.disabled = False

        self.ids.btn_user.disabled = False

        self.ids.btn_history.disabled = False

        # Accessing the recording_result attribute
        text = stt_handler_instance.recording_result

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

            self.ids.txt_output.text += f"\n\nUser Text:\n{
                text}\n\nDetected Sentiment: {Homepage.sentiment}"

            # Get the current day of the week
            day_of_week = datetime.now().strftime("%A")
            self.ids.txt_output.text += f"\n\nToday is {day_of_week}."

            # Get the local weather information
            weather_info = self.integration.get_weather_info(Homepage.location)
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
                personalized_feedback = self.integration.get_joke()
            elif 'news' in ltext:
                category = 'general'
                if 'sports' in ltext:
                    category = 'sports'
                elif 'tech' in ltext:
                    category = 'technology'
                elif 'entertainment' in ltext:
                    category = 'entertainment'
                personalized_feedback = self.integration.get_news(
                    category=category)
            elif 'weather' in ltext:
                personalized_feedback = self.integration.get_weather_info()
            elif 'trivia' in ltext:
                personalized_feedback = self.integration.get_trivia()
            elif 'quit' in ltext or 'done' in ltext or 'exit' in ltext or 'bye' in ltext:
                self.quit_app()
            else:
                text = f"give me in one or two lines for {text}"
                personalized_feedback = self.generate_personalized_feedback(
                    text, '', '')

        self.ids.txt_output.text += f"\n\nPersonalized Feedback:\n{
            personalized_feedback.replace('<br>', '')}"

        # Speak out the personalized feedback

        options = self.feedback_options(Homepage.sentiment)
        # self.ids.txt_output.text = self.ids.txt_output.text.replace('<br>', '')
        combined = personalized_feedback + options

        self.speak_out_feedback(combined)

        Homepage.isFirst = False

    def enable_buttons(self):
        self.ids.btn_record.disabled = False
        self.ids.btn_user.disabled = False
        self.ids.btn_history.disabled = False

    def quit_app(self):
        if platform == "win":
            # Quit the app gracefully
            self.speak_out_feedback("good bye")
            exit()
        elif platform == "android":
            # Quit the app gracefully
            self.speak_out_feedback("good bye")
            App.get_running_app().stop()

    def insert_history(self):
        try:
            db2 = EmotionDatabase()
            db2.insert_history_entry(Homepage.sentiment)
            db2.close_connection()
        except Exception as e:
            print(e)
            db2.close_connection()

    def feedback_options(self, sentiment):
        if Homepage.isFirst:
            feedback = "<br>I can tell a joke or <br> weather or <br> news or <br> motivational quote or <br> trivia or <br> anything else you would like to know. "
        else:
            feedback = "<br>Would you like to know about anything else?"

        return feedback

    def generate_personalized_feedback(self, text, weathertx,  day_of_week):
        # Use GPT-3 to generate personalized feedback
        userid = Homepage.username
        initial_prompt = f"user name={userid}, today is {
            day_of_week}, my weather is {weathertx}"
        if (Homepage.isFirst):
            prompt = f"Generate personalized feedback for the user's emotional feeling: {
                initial_prompt}, I feel {text}"
        else:
            prompt = text
        # get the feedback from openai
        feedback = self.integration.generate_openai_text(prompt)
        return feedback

    def speak_out_feedback(self, feedback):
        TTSHandler().speak_out_feedback(feedback)

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
