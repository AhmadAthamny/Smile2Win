import threading
from GUI import MainGUI
from Participant import Participant, ParticipantsList
from GameSetup import *
from speech_text import SpeechTexter
from face_recognition import faceRecognition


class GameCore:
    def __init__(self, min_participants):
        self.__Main_GUI = MainGUI(self)
        self.participants = ParticipantsList()
        self.__speech_recognizer = SpeechTexter()
        self.face_recognizer = faceRecognition()
        self.__game_setup = GameSetup(self)
        self.__participant_count = 0
        self.minimum_participants = min_participants

    def start_game(self):
        self.__Main_GUI.show_welcome_screen()
        self.__Main_GUI.start_gui()

    def extract_faces(self):
        self.extracting_thread = threading.Thread(target=self.extract_faces_job)
        self.extracting_thread.start()

    def extract_faces_job(self):
        self.face_recognizer.create_face_set()
        # We keep taking shots of the camera, until there are enough people in front of it.
        while True:
            img = self.__Main_GUI.take_shot()
            if self.__game_setup.extract_faces(img):
                break

            text = F"Waiting for at least {self.minimum_participants} person to be present.."
            self.__Main_GUI.update_welcome_statement(-1, text)

            time.sleep(5)

        self.__Main_GUI.names_setup()

        # Check if the number of the persons who are participating (who chose to play) is
        # more than the minimum number that was set.
        if not self.__game_setup.ask_for_names():
            # If the number of participants is less than the minimum, then we wait 6 seconds then stop the game.
            time.sleep(6)

            # Stop the GUI.
            self.__Main_GUI.stop_gui()

        # If name collecting was successful, we then need to know what's the game concept:
        self.__Main_GUI.end_names_setup()




    # This function is used by the GameSetup module.
    def display_face(self, img):
        self.__Main_GUI.display_face(img)

    # This function is used by the GameSetup module.
    def set_spoken_name(self, spoken_name):
        self.__Main_GUI.set_spoken_name(spoken_name)

    # This function is used by the GameSetup module.
    def show_mic_icon(self, toggle=True):
        self.__Main_GUI.start_listening(toggle)

    # This function is used by the GameSetup module.
    # It creates a new participant instance and adds it to the participants list of the game.
    def add_participant_to_game(self, faceid, face_img):
        new_participant = Participant()
        new_participant.set_faceId(faceid)
        new_participant.set_picture(face_img)
        self.participants.add_participant(new_participant)
        self.__participant_count += 1

    # Returns the count of the participants we have in the game.
    def participants_count(self):
        return self.__participant_count

    def recognize_speech(self):
        self.__speech_recognizer.run_recognizer()

    def recognizing_finished(self):
        return not self.__speech_recognizer.is_recognizing()

    def recognized_text(self):
        return self.__speech_recognizer.recognized_text()


if __name__ == '__main__':
    Core = GameCore(1)
    Core.start_game()
