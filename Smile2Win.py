import threading
from GUI import MainGUI
from Participant import Participant, ParticipantsList
from GameSetup import *
import speech_text
import vision

MAXIMUM_PLAYERS = 10

class GameCore:
    def __init__(self, min_participants):
        self.__Main_GUI = MainGUI(self)
        self.__participants = ParticipantsList()
        self.__speech_recognizer = speech_text.SpeechTexter()
        self.vision = vision.Vision(MAXIMUM_PLAYERS)
        self.__game_setup = GameSetup(self)
        self.minimum_participants = min_participants

    def start_game(self):
        self.__Main_GUI.show_welcome_screen()
        self.__Main_GUI.start_gui()

    def extract_faces(self):
        self.extracting_thread = threading.Thread(target=self.extract_faces_job)
        self.extracting_thread.daemon = True
        self.extracting_thread.start()

    def extract_faces_job(self):
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
            time.sleep(2)

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
        self.__Main_GUI.start_listening_names(toggle)

    # This function is used by the GameSetup module.
    # It creates a new participant instance and adds it to the participants list of the game.
    def add_participant_to_game(self, name, faceid, face_img):
        self.__participants.add_participant(name, faceid, face_img)

    def get_participant_from_name(self, name):
        return self.__participants.get_participant_from_name(name)
        
    def remove_participant(self, participant):
        self.__participants.remove_participant(participant)

    # Returns the count of the participants we have in the game.
    def participants_count(self):
        return self.__participants.get_participants_count()
    
    # Returns list of participants
    def get_all_participants(self):
        return self.__participants.get_all_participants()

    def recognize_speech(self):
        self.__speech_recognizer.run_recognizer()

    def recognizing_finished(self):
        return not self.__speech_recognizer.is_recognizing()

    def recognized_text(self):
        return self.__speech_recognizer.recognized_text()
    
    def inspect_participants_hands(self):
        img = self.__Main_GUI.take_shot()
        participants, encodings = self.__participants.get_participants_encodings()
        
        result = self.vision.find_next_turn(img, encodings)

        raising_hands = []
        for i in range(result):
            raising_hands.append(participants[i])

        return raising_hands
        

    def end_game(self):
        self.__speech_recognizer.stop_recognizer()
        exit()

if __name__ == '__main__':
    Core = GameCore(1)
    Core.start_game()
