from kivy.utils import platform
import time


class TTSHandler:
    def speak_out_feedback(self, message):
        if platform == "win":

            import pyttsx3

            self.text_to_speech_engine = pyttsx3.init()
            rate = self.text_to_speech_engine.getProperty('rate')
            self.text_to_speech_engine.setProperty('rate', 85)

            try:
                # If there is a <br> in the text, give it a few milliseconds pause.
                if ("<br>" in message):
                    segments = message.split('<br>')
                    for segment in segments:
                        # Replace any remaining <br> tags within the segment
                        segment = segment.replace('<br>', '')
                        if segment.strip():  # Check if the segment is not empty after removing <br>
                            print(f"Speaking segment: {segment}")
                            self.text_to_speech_engine.say(segment)
                            self.text_to_speech_engine.runAndWait()
                            # Introduce a pause between segments (you can adjust the duration)
                            time.sleep(0.5)
                # If there is no <br>, then there is no pause needed between segments
                else:
                    print(f"Speaking message: {message}")
                    self.text_to_speech_engine.say(message)
                    self.text_to_speech_engine.runAndWait()
                    time.sleep(0.05)
            finally:
                # Stop the TTS engine and release system resources
                self.text_to_speech_engine.stop()

        elif platform == "android":

            from jnius import autoclass

            Locale = autoclass('java.util.Locale')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            tts = TextToSpeech(PythonActivity.mActivity, None)

            content = message.replace('<br>', "...")

            tts.setLanguage(Locale.US)
            tts.speak(content, TextToSpeech.QUEUE_FLUSH, None)
