import requests

FACE_DETECTION_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"
FACE_SET_CREATION_URL = "https://api-us.faceplusplus.com/facepp/v3/faceset/create"
FACE_SET_ADD_FACE = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"
FACE_SET_REMOVE = "https://api-us.faceplusplus.com/facepp/v3/faceset/delete"


class faceRecognition:
    def __init__(self):
        self.__url = FACE_DETECTION_URL
        self.__faceset_token = None
        self.__API_KEY = "yNWSb95IUYlnLzblhfecvm65SOc8VepG"
        self.__SECRET_KEY = "shaBPQFkk76YZzs57DhGuNDFWo0NmwR7"


    def detect_faces(self, source_image, image_data):
        """
        :param source_image: The image taken from the camera.
        :param image_data: Base64
        :return: List of faces detect, each element of this form: tuple(face_token, face_img)
        """
        url = FACE_DETECTION_URL

        # Request parameters
        params = {
            'api_key': self.__API_KEY,
            'api_secret': self.__SECRET_KEY,
            'image_base64': image_data,
            'return_attributes': 'gender,age,smiling'
        }

        # Send the API request
        response = requests.post(url, data=params)

        # Parse the JSON response
        result = response.json()

        # Process the results
        faces_detected = []
        for face in result['faces']:
            face_rectangle = face['face_rectangle']

            cord_x1 = face_rectangle['left']
            cord_x2 = cord_x1 + face_rectangle['width']

            cord_y1 = face_rectangle['top']
            cord_y2 = cord_y1 + face_rectangle['height']

            face_img = source_image[max(cord_y1 - 60, 0): cord_y2,
                       max(cord_x1 - 30, 0): min(cord_x2 + 30, source_image.shape[1])]
            faces_detected.append((face['face_token'], face_img))

        return faces_detected


    def create_face_set(self):
        url = FACE_SET_CREATION_URL

        params = {
            'api_key': self.__API_KEY,
            'api_secret': self.__SECRET_KEY
        }

        response = requests.post(url, data=params)

        result = response.json()
        self.__faceset_token = result['faceset_token']


    def add_face_to_set(self, face_id):
        url = FACE_SET_ADD_FACE

        params = {
            'api_key': self.__API_KEY,
            'api_secret': self.__SECRET_KEY,
            'faceset_token': self.__faceset_token,
            'face_tokens': face_id
        }
        response = requests.post(url, data=params)
        result = response.json()
        if 'faceset_token' in result:
            return True
        return False


    def remove_face_set(self):
        url = FACE_SET_REMOVE

        params = {
            'api_key': self.__API_KEY,
            'api_secret': self.__SECRET_KEY,
            'faceset_token': self.__faceset_token,
            'check_empty': 0  # delete the faceset even if it contains face ids.
        }

        response = requests.post(url, data=params)
        result = response.json()
        if 'faceset_token' in result:
            return True
        return False
