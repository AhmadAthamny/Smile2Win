import face_recognition
import mediapipe as mp
import cv2
import numpy as np

class Vision:
    def __init__(self, max_hands, min_detection_confidence=0.7):
        """
        Initialize the Vision system with MediaPipe Hands for hand detection and
        other related settings.
        """
        self.max_hands = max_hands
        self.hands = mp.solutions.hands.Hands(max_num_hands=max_hands, min_detection_confidence=min_detection_confidence)

    def extract_faces(self, source_image):
        """
        Given a source image, extract face locations and their encodings.
        """
        rgb_image = source_image[:, :, ::-1]  # Convert BGR to RGB for face_recognition

        # Detect face locations and their encodings
        face_locations = face_recognition.face_locations(rgb_image)
        current_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        # Extract face images using the face locations
        face_images = []
        for (top, right, bottom, left) in face_locations:
            # Extract the face from the original image
            face_image = source_image[top:bottom, left:right]
            face_images.append(face_image)  # Append the cropped face image to the list

        return face_locations, current_encodings, face_images

    def __find_face_from_collection(self, collection_encodings, target_encoding):
        """
        Compare a target face encoding against a collection of known encodings.
        Returns the index of the matching face or -1 if no match is found.
        """
        matches = face_recognition.compare_faces(collection_encodings, target_encoding)

        for i, match in enumerate(matches):
            if match:
                return i
        return -1  # No match found

    def __is_open_palm(self, hand_landmarks):
        """
        Check if the detected hand is an open palm.
        """
        finger_tips = [mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
                       mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP,
                       mp.solutions.hands.HandLandmark.RING_FINGER_TIP,
                       mp.solutions.hands.HandLandmark.PINKY_TIP]

        finger_bases = [mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP,
                        mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP,
                        mp.solutions.hands.HandLandmark.RING_FINGER_MCP,
                        mp.solutions.hands.HandLandmark.PINKY_MCP]

        wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
        is_open = True

        # Check if fingers are extended
        for i in range(len(finger_tips)):
            tip = hand_landmarks.landmark[finger_tips[i]]
            base = hand_landmarks.landmark[finger_bases[i]]
            tip_base_distance = np.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
            if tip_base_distance < 0.1:
                is_open = False
                break

        # Check if fingers are spread
        if is_open:
            index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]

            if (np.linalg.norm(np.array([index_tip.x, index_tip.y]) - np.array([middle_tip.x, middle_tip.y])) < 0.05 or
                np.linalg.norm(np.array([middle_tip.x, middle_tip.y]) - np.array([ring_tip.x, ring_tip.y])) < 0.05 or
                np.linalg.norm(np.array([ring_tip.x, ring_tip.y]) - np.array([pinky_tip.x, pinky_tip.y])) < 0.05):
                is_open = False

        return is_open

    def __calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        """
        return np.linalg.norm(np.array(point1) - np.array(point2))

    def find_next_turn(self, source_image, players_encodings):
        """
        Given a source image, find which player raised their hand first by detecting
        hand positions and matching faces.
        """
        frame = cv2.flip(source_image, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Extract faces from the image
        face_locations, current_encodings = self.extract_faces(source_image)

        # Process the image to detect hands
        results = self.hands.process(rgb_frame)

        # List of faces with hands raised
        faces_with_hand = []

        # If hands are found
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if self.__is_open_palm(hand_landmarks):
                    hand_center = (hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].x,
                                   hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].y)

                    closest_face_index = -1
                    min_distance = float('inf')

                    # Loop over detected faces and compare proximity to the hand
                    for i, (top, right, bottom, left) in enumerate(face_locations):
                        # Calculate the center of the face
                        face_center = ((left + right) / 2, (top + bottom) / 2)

                        # Calculate the distance between the hand center and the face center
                        distance = self.__calculate_distance(hand_center, face_center)

                        # Track the closest face to the hand
                        if distance < min_distance:
                            min_distance = distance
                            closest_face_index = i

                    # If a face is close enough, check if we know it.
                    if closest_face_index != -1:
                        found_face = self.__find_face_from_collection(players_encodings, current_encodings[closest_face_index])
                        if found_face != -1:
                            faces_with_hand.append(found_face)

        return faces_with_hand