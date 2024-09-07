import requests


FACE_DETECTION_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"
FACE_SET_CREATION_URL = "https://api-us.faceplusplus.com/facepp/v3/faceset/create"
FACE_SET_ADD_FACE = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"
FACE_SET_REMOVE = "https://api-us.faceplusplus.com/facepp/v3/faceset/delete"

FACE_API_KEY = "yNWSb95IUYlnLzblhfecvm65SOc8VepG"
FACE_SECRET_KEY = "shaBPQFkk76YZzs57DhGuNDFWo0NmwR7"


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
