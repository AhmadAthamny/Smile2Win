import base64
import cv2
import time

from face_recognition import *
from intellegent_bot import parse_name_from_text


class GameSetup:
    def __init__(self, game_core):
        self.__game_core = game_core
        self.__face_recognizer = self.__game_core.face_recognizer
        self.__found = 0

    def extract_faces(self, img):
        buffer = cv2.imencode('.jpg', img)[1]
        base64_img = base64.b64encode(buffer).decode("utf-8")
        result = self.__face_recognizer.detect_faces(img, base64_img)

        # Check if there are at least two persons
        if len(result) < self.__game_core.minimum_participants:
            return False

        for face in result:
            self.__game_core.add_participant_to_game(face[0], face[1])
        return True

    def ask_for_names(self):
        # Count variable that holds the count of confirmed participants.
        # Confirmed participants which means people who their names were saved, and they will play.
        count = 0

        # Tells it's the first time waiting for the same person to talk.
        first_time = True

        # Pick a participant who wasn't asked for a name yet.
        p = self.__game_core.participants.get_participant_from_name(None)
        while p:
            self.__game_core.show_mic_icon(0)

            if first_time:
                self.__game_core.display_face(p.get_picture())
                self.__game_core.set_spoken_name("Participant #" + str(count + 1) + " Name")
                first_time = False

            self.listen_participant_name(p)
            p = self.__game_core.participants.get_participant_from_name(None)

        # Process finished successfully.
        return True

    def listen_participant_name(self, participant):
        # A small delay before recording voice.
        time.sleep(2)
        self.__game_core.show_mic_icon()
        self.__game_core.recognize_speech()
        while not self.__game_core.recognizing_finished():
            time.sleep(1)

        self.__game_core.show_mic_icon(False)

        speaker_text = self.__game_core.recognized_text()

        # We make sure we got some text from the speaker
        if speaker_text is None or len(speaker_text) == 0:
            self.__game_core.set_spoken_name("Please say your name again! :)")
            self.listen_participant_name(participant)
        else:
            # We interpret the text with our intelligent bot.
            parsed_name = parse_name_from_text(speaker_text)

            # not playing
            if parsed_name == (False, 0):
                self.__game_core.set_spoken_name("Not participating :(")
                self.__game_core.participants.remove_participant(participant)

            # no name found in the spoken text.
            elif parsed_name == (False, 1):
                self.__game_core.set_spoken_name("Please say your name again! :)")
                self.listen_participant_name(participant)

            # else, we got the name:
            else:
                participant.set_name(parsed_name[1])
                # Add the person to the faceset, so we can remember his faceid later.
                face_id = participant.get_faceId()
                self.__face_recognizer.add_face_to_set(face_id)
