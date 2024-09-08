import time

from intellegent_bot import parse_name_from_text


class GameSetup:
    def __init__(self, game_core):
        self.__game_core = game_core
        self.__vision = self.__game_core.vision

    def extract_faces(self, img):
        current_encodings, face_images = self.__vision.extract_faces(img)

        # Check if there is minimum count of participants.
        if len(current_encodings) < self.__game_core.minimum_participants:
            return False
        

        for i in range(len(current_encodings)):
            self.__game_core.add_participant_to_game(None, current_encodings[i], face_images[i])
        return True

    def ask_for_names(self):
        p_num = 0

        # Pick a participant who wasn't asked for a name yet.
        p = self.__game_core.get_participant_from_name(None)
        while p:
            p_num += 1
            self.__game_core.show_mic_icon(0)
            self.__game_core.display_face(p.get_picture())
            self.__game_core.set_spoken_name("Participant #" + str(p_num) + " Name")
            self.listen_participant_name(p)

            p = self.__game_core.get_participant_from_name(None)

        # Process finished successfully.
        # Check if we have the minimum players.
        if self.__game_core.participants_count() < self.__game_core.minimum_participants:
            self.__game_core.set_spoken_name("Not enough players, game ending.")
            return False
        
        # Else, we are good to go.
        return True

    def listen_participant_name(self, participant):
        # A small delay before recording voice.
        time.sleep(2)
        self.__game_core.show_mic_icon()
        self.__game_core.recognize_speech()
        while not self.__game_core.recognizing_finished():
            time.sleep(0.5)
            self.__game_core.set_spoken_name(self.__game_core.recognized_text())

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
                self.__game_core.remove_participant(participant)
                time.sleep(1.5)

            # no name found in the spoken text.
            elif parsed_name == (False, 1):
                self.__game_core.set_spoken_name("Please say your name again! :)")
                self.listen_participant_name(participant)

            # else, we got the name:
            else:
                participant.set_name(parsed_name[1])
                self.__game_core.set_spoken_name("Hi " + parsed_name[1])
                time.sleep(1.5)
