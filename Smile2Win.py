import threading
from GUI import MainGUI
from Participant import Participant, ParticipantsList
from GameSetup import *


class GameCore:
    def __init__(self, min_participants):
        self.__Main_GUI = MainGUI(self)
        self.participants = ParticipantsList()
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
        while True:
            img = self.__Main_GUI.take_shot()
            if self.__game_setup.extract_faces(img):
                break
            self.__Main_GUI.update_welcome_statement(4)
            time.sleep(10)

        self.__Main_GUI.names_setup()
        if not self.__game_setup.ask_for_names():
            time.sleep(6)
            self.__Main_GUI.stop_gui()

    def display_face(self, img):
        self.__Main_GUI.display_face(img)

    def set_spoken_name(self, spoken_name):
        self.__Main_GUI.set_spoken_name(spoken_name)

    def show_mic_icon(self, toggle=True):
        self.__Main_GUI.start_listening(toggle)

    def add_participant_to_game(self, faceid, face_img):
        new_participant = Participant()
        new_participant.set_faceId(faceid)
        new_participant.set_picture(face_img)
        self.participants.add_participant(new_participant)
        self.__participant_count += 1


    def participants_count(self):
        return self.__participant_count


if __name__ == '__main__':
    Core = GameCore(2)
    Core.start_game()
