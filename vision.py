import face_recognition
import mediapipe as mp
import cv2

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
    for encoding in collection_encodings:
        # Compare current encoding with target_encoding
        match = face_recognition.compare_faces()

def findNextTurn(source_image, current_encodings, max_hands):

    frame = cv2.flip(source_image, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Initialize mp library detection
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=max_hands, min_detection_confidence=0.7)
    face_locations, current_encodings = extractFaces(source_image)

    # Process the image to detect hands
    results = hands.process(rgb_frame)

    # Holds array for all faces that have a hand raised.
    faces_with_hand = []

    # If hands found
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hands_landmarks:
            # Compute the palm center as the average of these points
            palm_x = (wrist.x + index_finger_mcp.x + pinky_mcp.x) / 3
            palm_y = (wrist.y + index_finger_mcp.y + pinky_mcp.y) / 3

            # Get pixel coordinates (since landmarks are normalized to [0, 1])
            h, w, _ = frame.shape
            palm_center_pixel = (int(palm_x * w), int(palm_y * h))

            # Now, check distance from closest head.
            for face_location in face_locations:

            
    else:
        # No gestures found
        return False



def is_open_palm(hand_landmarks):
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