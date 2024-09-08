from threading import Thread
import azure.cognitiveservices.speech as speechsdk


class SpeechTexter:
    def __init__(self):
        # Configurations
        self.__AZURE_SPEECH_KEY = "27ad332875fe4a9eba0e59bb0cb07686"
        self.__AZURE_REGION = "westeurope"

        speech_config = speechsdk.SpeechConfig(subscription=self.__AZURE_SPEECH_KEY, region=self.__AZURE_REGION)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.__speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Connect the events to the handlers
        self.__speech_recognizer.recognizing.connect(self.__recognizing_handler)  # Partial results in real-time
        self.__speech_recognizer.recognized.connect(self.__recognized_handler)  # Final results after speech ends

        # These will be tracked from external modules.
        self.__recognized_text = ""
        self.__recognizing = False

    # Handler for the continuous listening.
    def __recognizing_handler(self, evt):
        self.__recognized_text = evt.result.text

    # Handles the end of the listening
    def __recognized_handler(self, evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            self.__recognized_text = evt.result.text
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            self.__recognized_text = None

        self.__recognizing = False
        self.__speech_recognizer.stop_continuous_recognition_async()

    def __start_speech_recognition(self):
        print("startinggg")
        # Start continuous recognition
        self.__speech_recognizer.start_continuous_recognition_async()

        # Keep the recognizer running until no more words coming.
        while self.__recognizing:
            pass

    def run_recognizer(self):
        if not self.__recognizing:
            self.__recognized_text = ""
            # Thread for running the speech recognition
            speech_thread = Thread(target=self.__start_speech_recognition)
            speech_thread.daemon = True

            self.__recognizing = True
            speech_thread.start()

    def is_recognizing(self):
        return self.__recognizing

    def recognized_text(self):
        return self.__recognized_text
