import face_recognition
import mediapipe as mp
import cv2
import numpy as np


# Initialize mp library detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=max_hands, min_detection_confidence=0.7)

def extractFaces(source_image):
    """
    Given a source image, it parses faces, return faces locations and their encodings.
    """
    extracted_faces = []
    rgb_image = source_image[:, :, ::-1]

    # Detect face locations in the frame
    face_locations = face_recognition.face_locations(rgb_image)
    current_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    return face_locations, current_encodings

def findFaceFromCollection(collection_encodings, target_encoding):
    matches = face_recognition.compare_faces(collection_encodings, target_encoding)

    # Looping over matches:
    for i, match in enumerate(matches):
        if match:
            return i
    return -1

def findNextTurn(source_image, players_encodings, max_hands):
    frame = cv2.flip(source_image, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations, current_encodings = extractFaces(source_image)

    # Process the image to detect hands
    results = hands.process(rgb_frame)

    # Holds array for all faces that have a hand raised.
    faces_with_hand = []

    # If hands found
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            if is_open_palm(hand_landmarks, max_hands):
                hand_center = (hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x, 
                    hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)

                closest_face_index = -1
                min_distance = float('inf')

                # Loop over detected faces and compare proximity to the hand
                for i, (top, right, bottom, left) in enumerate(face_locations):
                    # Calculate the center of the face
                    face_center = ((left + right) / 2, (top + bottom) / 2)

                    # Calculate the distance between the hand center and the face center
                    distance = calculate_distance(hand_center, face_center)

                    # Keep track of the closest face
                    if distance < min_distance:
                        min_distance = distance
                        closest_face_index = i

                # If a face is close enough, check if we know it.
                if closest_face_index != -1:
                    found_face = findFaceFromCollection(players_encodings, current_encodings[closest_face_index])
                    if found_face != -1:
                        faces_with_hand.append(found_face)
                
    return faces_with_hand

def is_open_palm(hand_landmarks, max_hands):
    # Indices for finger tips and their corresponding base joints
    finger_tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                   mp_hands.HandLandmark.RING_FINGER_TIP,
                   mp_hands.HandLandmark.PINKY_TIP]

    finger_bases = [mp_hands.HandLandmark.INDEX_FINGER_MCP,
                    mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                    mp_hands.HandLandmark.RING_FINGER_MCP,
                    mp_hands.HandLandmark.PINKY_MCP]

    # Wrist landmark
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # Calculate distances between finger tips and the base of the hand
    is_open = True
    for i in range(len(finger_tips)):
        tip = hand_landmarks.landmark[finger_tips[i]]
        base = hand_landmarks.landmark[finger_bases[i]]

        # Calculate Euclidean distance between finger tips and the base
        tip_base_distance = np.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
        if tip_base_distance < 0.1:  # Check if the distance is too small (fingers not extended)
            is_open = False
            break

    # Additional condition: Check if the fingers are spread (distance between adjacent fingers)
    if is_open:
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

        # Finger spread condition (fingers should not overlap or be too close)
        if (np.linalg.norm(np.array([index_tip.x, index_tip.y]) - np.array([middle_tip.x, middle_tip.y])) < 0.05 or
            np.linalg.norm(np.array([middle_tip.x, middle_tip.y]) - np.array([ring_tip.x, ring_tip.y])) < 0.05 or
            np.linalg.norm(np.array([ring_tip.x, ring_tip.y]) - np.array([pinky_tip.x, pinky_tip.y])) < 0.05):
            is_open = False

    return is_open

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))