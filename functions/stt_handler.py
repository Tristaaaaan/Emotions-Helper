from kivy.utils import platform
import time
from kivy.clock import mainthread


class STTHandler:

    def __init__(self, callback=None):
        self.recording_result = None

    def getAudioText(self):
        # Android Platform
        if platform == "android":
            from functions.speech_events import SpeechEvents
            from jnius import autoclass

            self.speech_events = SpeechEvents()

            self.speech_events.create_recognizer(
                self.recognizer_event_handler())

            if self.speech_events:

                self.unwrapped = ''

                self.speech_events.start_listening()

            countdown_seconds = 10

            for i in range(countdown_seconds, 0, -1):
                print(i)
                time.sleep(1)

            print("Timer expired. Executing code now.")

            self.speech_events.stop_listening()

            self.recording_result = self.unwrapped

        # Windows Platform
        elif platform == 'win':
            text = 'I am so happy!'
            self.recording_result = text
            # import speech_recognition as sr

            # recognizer = sr.Recognizer()
            # with sr.Microphone() as source:
            #     recognizer.adjust_for_ambient_noise(source)
            #     try:
            #         audio_data = recognizer.listen(source, timeout=10)
            #         text = recognizer.recognize_google(audio_data)

            #         self.recording_result = text
            #     except Exception as e:
            #         print(e)

    @mainthread
    def recognizer_event_handler(self, key, value):
        if key == 'onReadyForSpeech':
            pass
        elif key == 'onBeginningOfSpeech':
            pass
        elif key == 'onEndOfSpeech':
            pass
        elif key == 'onError':
            self.speech_events.stop_listening()
            self.speech_events.destroy_recognizer()
            if self.callback:
                self.callback()

        elif key in ['onPartialResults', 'onResults']:
            self.unwrapped = str(value)
        elif key in ['onBufferReceived', 'onEvent', 'onRmsChanged']:
            pass
