import base64
import cv2
import requests
import time
from speech_text import recognize_from_microphone
from intellegent_bot import parse_name_from_text

FACE_DETECTION_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"
FACE_SET_CREATION_URL = "https://api-us.faceplusplus.com/facepp/v3/faceset/create"
FACE_SET_ADD_FACE = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"
FACE_SET_REMOVE = "https://api-us.faceplusplus.com/facepp/v3/faceset/delete"

FACE_API_KEY = "yNWSb95IUYlnLzblhfecvm65SOc8VepG"
FACE_SECRET_KEY = "shaBPQFkk76YZzs57DhGuNDFWo0NmwR7"


class GameSetup:
    def __init__(self, game_core):
        self.__game_core = game_core
        self.__found = 0
        self.__faceset_token = None

    def extract_faces(self, img):
        self.__faceset_token = create_face_set(FACE_API_KEY, FACE_SECRET_KEY)

        buffer = cv2.imencode('.jpg', img)[1]
        base64_img = base64.b64encode(buffer).decode("utf-8")
        result = detect_faces(FACE_API_KEY, FACE_SECRET_KEY, base64_img)

        # Check if there are at least two persons
        if len(result['faces']) < self.__game_core.minimum_participants:
            return False

        # Process the results
        for face in result['faces']:
            face_rectangle = face['face_rectangle']

            cord_x1 = face_rectangle['left']
            cord_x2 = cord_x1 + face_rectangle['width']

            cord_y1 = face_rectangle['top']
            cord_y2 = cord_y1 + face_rectangle['height']

            face_img = img[max(cord_y1 - 60, 0): cord_y2, max(cord_x1 - 30, 0): min(cord_x2 + 30, img.shape[1])]
            self.__game_core.add_participant_to_game(face['face_token'], face_img)
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

            # A small delay before recording voice.
            time.sleep(3)
            self.__game_core.show_mic_icon(1)
            result = recognize_from_microphone()
            self.__game_core.show_mic_icon(0)

            # If we couldn't recognize what the person said
            if not result[0]:
                self.__game_core.set_spoken_name("Please say your name again! :)")

            # If we got speech recognized, we process it with ChatGPT:
            else:
                recognized_text = result[1]
                print(recognized_text)

                # Parse the name said in the recognized speech.
                parsed_name = parse_name_from_text(recognized_text)

                # ChatGPT couldn't understand what the user is trying to say.
                # In this case, we repeat the same process for the same person.
                if parsed_name == (False, 1):
                    self.__game_core.set_spoken_name("Please say your name again! :)")
                    continue

                # The user states that he doesn't want to participate.
                elif parsed_name == (False, 0):
                    self.__game_core.set_spoken_name("Not participating :(")
                    self.__game_core.participants.remove_participant(p)

                # ChatGPT successfully parses the name of the person from the recognized speech.
                else:
                    # Add the person to the faceset, so we can remember his faceid later.
                    face_id = p.get_faceId()
                    add_face_to_set(FACE_API_KEY, FACE_SECRET_KEY, self.__faceset_token, face_id)

                    # Update the participant's name on the GUI.
                    parsed_name = parsed_name[1]
                    self.__game_core.set_spoken_name(parsed_name)

                    # Update the participant's instance name.
                    p.set_name(parsed_name)

                    # We inform the user of successfully saving his name.
                    self.__game_core.show_mic_icon(2)
                    count += 1

                # We search for a participant that has no name yet.
                p = self.__game_core.participants.get_participant_from_name(None)
                first_time = True
                time.sleep(3)

        # After having the number of participants, we check if they meet the minimum requirement.
        if count < self.__game_core.minimum_participants:
            self.__game_core.set_spoken_name("Not enough participants\nStart the game when ready! :)")
            return False

        # Process finished successfully.
        return True


# Helper function to parse faces
def detect_faces(api_key, api_secret, image_data):
    url = FACE_DETECTION_URL

    # Request parameters
    params = {
        'api_key': api_key,
        'api_secret': api_secret,
        'image_base64': image_data,
        'return_attributes': 'gender,age,smiling'  # Optional: include additional attributes
    }

    # Send the API request
    response = requests.post(url, data=params)

    # Parse the JSON response
    return response.json()


def create_face_set(api_key, api_secret):
    url = FACE_SET_CREATION_URL

    params = {
        'api_key': api_key,
        'api_secret': api_secret
    }

    response = requests.post(url, data=params)

    result = response.json()
    return result['faceset_token']


def add_face_to_set(api_key, api_secret, faceset_id, face_id):
    url = FACE_SET_ADD_FACE

    params = {
        'api_key': api_key,
        'api_secret': api_secret,
        'faceset_token': faceset_id,
        'face_tokens': face_id
    }
    response = requests.post(url, data=params)
    result = response.json()
    if 'faceset_token' in result:
        return True
    return False


def remove_face_set(api_key, api_secret, faceset):
    url = FACE_SET_REMOVE

    params = {
        'api_key': api_key,
        'api_secret': api_secret,
        'faceset_token': faceset,
        'check_empty': 0  # delete the faceset even if it contains face ids.
    }

    response = requests.post(url, data=params)
    result = response.json()
    if 'faceset_token' in result:
        return True
    return False
