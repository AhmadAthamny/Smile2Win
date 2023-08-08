import base64
import cv2
import requests
import time
from speech_text import recognize_from_microphone
from intellegent_bot import parse_name_from_text

FACE_DETECTION_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"
FACE_SET_CREATION_URL = "https://api-us.faceplusplus.com/facepp/v3/faceset/create"
FACE_SET_ADD_FACE = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"

FACE_API_KEY = "yNWSb95IUYlnLzblhfecvm65SOc8VepG"
FACE_SECRET_KEY = "shaBPQFkk76YZzs57DhGuNDFWo0NmwR7"


class RegisterParticipants:
    def __init__(self, game_core):
        self.__game_core = game_core
        self.__found = 0
        self.__faceset_token = None

    def extract_faces(self, img):
        self.__faceset_token = create_face_set(FACE_API_KEY, FACE_SECRET_KEY)

        buffer = cv2.imencode('.jpg', img)[1]
        base64_img = base64.b64encode(buffer).decode("utf-8")
        result = detect_faces(FACE_API_KEY, FACE_SECRET_KEY, base64_img)

        # Process the results
        for face in result['faces']:
            face_rectangle = face['face_rectangle']

            cord_x1 = face_rectangle['left']
            cord_x2 = cord_x1 + face_rectangle['width']

            cord_y1 = face_rectangle['top']
            cord_y2 = cord_y1 + face_rectangle['height']

            face_img = img[max(cord_y1 - 60, 0): cord_y2, max(cord_x1 - 30, 0): min(cord_x2 + 30, img.shape[1])]

            add_face_to_set(FACE_API_KEY, FACE_SECRET_KEY, self.__faceset_token, face['face_token'])
            self.__game_core.add_participant_to_game(face['face_token'], face_img)

    def ask_for_names(self):
        p = self.__game_core.participants.get_participant_from_name(None)
        count = 0
        first_time = True
        while p:
            self.__game_core.show_mic_icon(0)
            if first_time:
                self.__game_core.display_face(p.get_picture())
                self.__game_core.set_spoken_name("Participant #" + str(count + 1) + " Name")
                first_time = not first_time
            time.sleep(3)
            self.__game_core.show_mic_icon(1)
            result = recognize_from_microphone()
            self.__game_core.show_mic_icon(0)
            if not result[0]:
                self.__game_core.set_spoken_name("Please say your name again! :)")
            else:
                recognized_text = result[1]
                print(recognized_text)
                parsed_name = parse_name_from_text(recognized_text)
                if parsed_name is None:
                    self.__game_core.set_spoken_name("Please say your name again! :)")
                    continue
                print(parsed_name)
                p.set_name(parsed_name)
                self.__game_core.set_spoken_name(parsed_name)
                self.__game_core.show_mic_icon(2)
                p = self.__game_core.participants.get_participant_from_name(None)
                count += 1
                first_time = True
                time.sleep(3)


# Helper function to parse faces
def detect_faces(api_key, api_secret, image_data):
    # Face++ API endpoint for face detection
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
