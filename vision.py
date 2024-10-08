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
        Given a source image, extract face images and their encodings.
        """
        
        # Convert BGR (from VideoCapture) to RGB (for face_recognition)
        rgb_image = cv2.cvtColor(source_image, cv2.COLOR_BGR2RGB)

        # Detect face locations and their encodings
        face_locations = face_recognition.face_locations(rgb_image)
        current_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        # Extract face images using the face locations
        face_images = []
        for (top, right, bottom, left) in face_locations:
            # Extract the face from the original image
            top = max(0, top - int((bottom - top) * 0.7))
            bottom = min(source_image.shape[0], bottom + int((bottom - top) * 0.2))
            left = max(0, left - int((right-left) * 0.2))
            right = min(source_image.shape[1], right + int((right-left) * 0.2))

            # Extract the face with padding from the original image
            face_image = source_image[top:bottom, left:right]
            face_images.append(face_image)  # Append the cropped face image to the list

        return face_locations, current_encodings, face_images

    def __find_face_from_collection(self, collection_encodings: list, target_encoding: np.ndarray, tolerance: float = 0.8) -> int:
        """
        Compare a target face encoding against a collection of known encodings using face distance.
        Returns the index of the closest matching face or -1 if no match is found.
        """
        # Compute face distances between the target encoding and all known encodings
        distances = face_recognition.face_distance(collection_encodings, target_encoding)

        # Find the index of the closest face by distance
        best_match_index = np.argmin(distances)

        # Check if the closest face is within the tolerance range
        if distances[best_match_index] <= tolerance:
            return best_match_index
        else:
            return -1  # No match found within the tolerance

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

        return is_open

    def __calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        """
        return np.linalg.norm(np.array(point1) - np.array(point2))

    def find_next_turn(self, source_image: np.ndarray, players_encodings: list) -> list:
        """
        Given a source image, find which player raised their hand first by detecting
        hand positions and matching faces.
        
        Args:
            source_image (np.ndarray): The input image from the camera feed.
            players_encodings (list): List of known player face encodings.
        
        Returns:
            list: Indices of the players with their hand raised, based on proximity to face and hand position.
        """
        # Flip the image horizontally for a more natural camera view
        frame = cv2.flip(source_image, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_height, frame_width, _ = frame.shape

        # Extract faces from the flipped image (frame)
        face_locations, current_encodings, _ = self.extract_faces(frame)

        # Process the image to detect hands
        results = self.hands.process(rgb_frame)

        # List of player indices with raised hands
        faces_with_hand = []

        # If hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Check if the hand is an open palm (signal for raised hand)
                if self.__is_open_palm(hand_landmarks):
                    # Get the wrist coordinates as the hand center
                    hand_center = (hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].x,
                                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].y)
                    hand_center = hand_center[0] * frame_width, hand_center[1] * frame_height

                    closest_face_index = -1
                    min_distance = float('inf')

                    # Loop over detected faces to find the closest one to the raised hand
                    for i, (top, right, bottom, left) in enumerate(face_locations):
                        # Calculate the center of the face
                        face_center = ((left + right) / 2, (top + bottom) / 2)

                        # Calculate the distance between the hand center and the face center
                        distance = self.__calculate_distance(hand_center, face_center)
                        # Track the closest face to the hand
                        if distance < min_distance:
                            min_distance = distance
                            closest_face_index = i
                    # If a close face is found, check if it matches a known player encoding
                    if closest_face_index != -1 and closest_face_index < len(current_encodings):
                        # Use face distance to find the closest match
                        found_face = self.__find_face_from_collection(players_encodings, current_encodings[closest_face_index])
                        
                        if found_face != -1:
                            faces_with_hand.append(found_face)

        return faces_with_hand
